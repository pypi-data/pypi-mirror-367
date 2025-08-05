/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

use std::iter;
use std::path::Path;
use std::path::PathBuf;

use pyrefly_python::module_name::ModuleName;
use pyrefly_python::module_path::ModulePath;
use ruff_python_ast::name::Name;
use starlark_map::small_map::SmallMap;
use vec1::Vec1;

use crate::config::config::ConfigFile;
use crate::module::typeshed::typeshed;
use crate::state::loader::FindError;

#[derive(Debug, PartialEq)]
enum FindResult {
    /// Found a single-file .pyi module. The path must not point to an __init__ file.
    SingleFilePyiModule(PathBuf),
    /// Found a single-file .py module. The path must not point to an __init__ file.
    SingleFilePyModule(PathBuf),
    /// Found regular packages. First path must point to an __init__ file.
    /// Second path indicates where to continue search next. It should always point to the parent of the __init__ file.
    /// The ordering of packages should be the same as the order they're found
    /// in the `includes`.
    RegularPackage(PathBuf, PathBuf),
    /// Found a namespace package.
    /// The path component indicates where to continue search next. It may contain more than one directories as the namespace package
    /// may span across multiple search roots.
    NamespacePackage(Vec1<PathBuf>),
    /// Found a compiled Python file (.pyc, .pyx, .pyd). Represents some kind of
    /// compiled module, whether that's bytecode, C extension, or DLL.
    /// Compiled modules lack source and type info, and are
    /// treated as `typing.Any` to handle imports without type errors.
    CompiledModule(PathBuf),
}

impl FindResult {
    fn single_file(path: PathBuf, ext: &str) -> Self {
        if ext == "pyi" {
            Self::SingleFilePyiModule(path)
        } else {
            Self::SingleFilePyModule(path)
        }
    }
}

/// In the given root, attempt to find a match for the given [`Name`].
fn find_one_part_in_root(name: &Name, root: &Path) -> Option<FindResult> {
    let candidate_dir = root.join(name.as_str());
    // First check if `name` corresponds to a regular package.
    for candidate_init_suffix in ["__init__.pyi", "__init__.py"] {
        let init_path = candidate_dir.join(candidate_init_suffix);
        if init_path.exists() {
            return Some(FindResult::RegularPackage(init_path, candidate_dir));
        }
    }
    // Second check if `name` corresponds to a single-file module.
    for candidate_file_suffix in ["pyi", "py"] {
        let candidate_path = root.join(format!("{name}.{candidate_file_suffix}"));
        if candidate_path.exists() {
            return Some(FindResult::single_file(
                candidate_path,
                candidate_file_suffix,
            ));
        }
    }
    // Check if `name` corresponds to a compiled module.
    for candidate_compiled_suffix in ["pyc", "pyx", "pyd"] {
        let candidate_path = root.join(format!("{name}.{candidate_compiled_suffix}"));
        if candidate_path.exists() {
            return Some(FindResult::CompiledModule(candidate_path));
        }
    }
    // Finally check if `name` corresponds to a namespace package.
    if candidate_dir.is_dir() {
        return Some(FindResult::NamespacePackage(Vec1::new(candidate_dir)));
    }
    None
}

/// Finds the first package (regular, single file, or namespace) in all search roots.
/// Returns None if no module is found. If `name` is `__pycache__`, we always
/// return `None`.
fn find_one_part<'a>(name: &Name, roots: impl Iterator<Item = &'a PathBuf>) -> Option<FindResult> {
    // skip looking in `__pycache__`, since those modules are not accessible
    if name == &Name::new_static("__pycache__") {
        return None;
    }
    let mut namespace_roots = Vec::new();
    for root in roots {
        match find_one_part_in_root(name, root) {
            None => (),
            Some(FindResult::NamespacePackage(package)) => {
                namespace_roots.push(package.first().clone())
            }
            result @ Some(FindResult::RegularPackage(..)) => return result,
            result @ Some(_) => return result,
        }
    }
    match Vec1::try_from_vec(namespace_roots) {
        Err(_) => None,
        Ok(namespace_roots) => Some(FindResult::NamespacePackage(namespace_roots)),
    }
}

/// Finds the first package (regular, single file, or namespace) in search roots. Returns None if no module is found.
/// name: module name
/// roots: search roots
fn find_one_part_prefix<'a>(
    prefix: &Name,
    roots: impl Iterator<Item = &'a PathBuf>,
) -> Vec<(FindResult, ModuleName)> {
    let mut results = Vec::new();
    let mut namespace_roots: SmallMap<ModuleName, Vec<PathBuf>> = SmallMap::new();

    for root in roots {
        // List all entries in the root directory
        if let Ok(entries) = std::fs::read_dir(root) {
            for entry in entries.filter_map(Result::ok) {
                let path = entry.path();
                let file_name = path.file_name().and_then(|n| n.to_str());

                if let Some(name) = file_name {
                    // Check if the name starts with the prefix
                    if name.starts_with(prefix.as_str()) {
                        // Check if it's a regular package
                        if path.is_dir() {
                            for candidate_init_suffix in ["__init__.pyi", "__init__.py"] {
                                let init_path = path.join(candidate_init_suffix);
                                if init_path.exists() {
                                    results.push((
                                        FindResult::RegularPackage(init_path, path.clone()),
                                        ModuleName::from_str(name),
                                    ));
                                    break;
                                }
                            }

                            if !results.iter().any(|r| match r {
                                (FindResult::RegularPackage(_, p), _) => p == &path,
                                _ => false,
                            }) {
                                namespace_roots
                                    .entry(ModuleName::from_str(name))
                                    .or_default()
                                    .push(path.clone());
                            }
                        } else if let Some((stem, ext)) = name.rsplit_once('.')
                            && ["pyi", "py"].contains(&ext)
                            && !["__init__", "__main__"].contains(&stem)
                            && path.is_file()
                        {
                            results.push((
                                FindResult::single_file(path.clone(), ext),
                                ModuleName::from_str(stem),
                            ));
                        }
                    }
                }
            }
        }
    }

    // Add namespace packages to results
    for (name, roots) in namespace_roots {
        if let Ok(namespace_roots) = Vec1::try_from_vec(roots) {
            results.push((FindResult::NamespacePackage(namespace_roots), name));
        }
    }

    // todo: also return modulename so we know what to call this
    results
}

/// Find a module from a single package. Returns None if no module is found.
fn continue_find_module(
    start_result: FindResult,
    components_rest: &[Name],
) -> Result<Option<ModulePath>, FindError> {
    let mut current_result = Some(start_result);
    for part in components_rest.iter() {
        match current_result {
            None => {
                // Nothing has been found in the previous round. No point keep looking.
                break;
            }
            Some(FindResult::SingleFilePyiModule(_))
            | Some(FindResult::SingleFilePyModule(_))
            | Some(FindResult::CompiledModule(_)) => {
                // We've already reached leaf nodes. Cannot keep searching
                current_result = None;
                break;
            }
            Some(FindResult::RegularPackage(_, next_root)) => {
                current_result = find_one_part(part, [next_root].iter());
            }
            Some(FindResult::NamespacePackage(next_roots)) => {
                current_result = find_one_part(part, next_roots.iter());
            }
        }
    }
    current_result.map_or(Ok(None), |x| match x {
        FindResult::SingleFilePyiModule(path)
        | FindResult::SingleFilePyModule(path)
        | FindResult::RegularPackage(path, _) => Ok(Some(ModulePath::filesystem(path))),
        FindResult::NamespacePackage(roots) => {
            // TODO(grievejia): Preserving all info in the list instead of dropping all but the first one.
            Ok(Some(ModulePath::namespace(roots.first().clone())))
        }
        FindResult::CompiledModule(_) => Err(FindError::Ignored),
    })
}

/// Search for the given [`ModuleName`] in the given `include`, which is
/// a list of paths denoting import roots. A [`FindError`] result indicates
/// searching should be discontinued because of a special condition, whereas
/// an `Ok(None)` indicates the module wasn't found here, but could be found in another
/// search location (`site_package_path`, `typeshed`, ...).
///
/// `search_path` differs from `site_package_path` in two ways:
/// 1. meaning: `search_path` *should* be project files, while `site_package_path`
///    should be third-party imports
/// 2. import resolution: `site_package_path` has extra checks that can occur, while `search_path`
///    is just a 'find and return the first result' search.
fn find_module_in_search_path<'a, I>(
    module: ModuleName,
    include: I,
) -> Result<Option<ModulePath>, FindError>
where
    I: Iterator<Item = &'a PathBuf> + Clone,
{
    match module.components().as_slice() {
        [] => Ok(None),
        [first, rest @ ..] => {
            // First try finding the module in `-stubs`.
            let stub_first = Name::new(format!("{first}-stubs"));
            let stub_result = find_one_part(&stub_first, include.clone())
                .map(|start_result| continue_find_module(start_result, rest))
                .transpose()?
                .flatten();
            if let Some(stub_result) = stub_result {
                return Ok(Some(stub_result));
            }

            // If we couldn't find it in a `-stubs` module, look normally.
            let result = find_one_part(first, include)
                .and_then(|start_result| continue_find_module(start_result, rest).transpose())
                .transpose()?;
            Ok(result)
        }
    }
}

/// Search for the given [`ModuleName`] in the given `include`, which is
/// a list of paths denoting import roots. A [`FindError`] result indicates
/// searching should be discontinued because of a special condition, whereas
/// an `Ok(None)` indicates the module wasn't found here, but could be found in another
/// search location (`search_path`, `typeshed`, ...).
///
/// `search_path` differs from `site_package_path` in two ways:
/// 1. meaning: `search_path` *should* be project files, while `site_package_path`
///    should be third-party imports
/// 2. import resolution: `site_package_path` has extra checks that can occur, while `search_path`
///    is just a 'find and return the first result' search.
fn find_module_in_site_package_path<'a, I>(
    module: ModuleName,
    include: I,
    ignore_missing_source: bool,
) -> Result<Option<ModulePath>, FindError>
where
    I: Iterator<Item = &'a PathBuf> + Clone,
{
    let components = module.components();
    let first = &components[0];
    let rest = &components[1..];
    let stub_first = Name::new(format!("{first}-stubs"));

    let stub_module_imports = include
        .clone()
        .filter_map(|root| find_one_part(&stub_first, iter::once(root)));

    let mut found_stubs = None;
    for stub_module_import in stub_module_imports {
        if let Some(stub_result) = continue_find_module(stub_module_import, rest)? {
            found_stubs = Some(stub_result);
            break;
        }
    }

    if found_stubs.is_some() && ignore_missing_source {
        return Ok(found_stubs);
    }

    let mut fallback_modules = include
        .clone()
        .filter_map(|root| find_one_part(first, iter::once(root)))
        .peekable();

    // check if there's an existing library backing the stubs we have
    if found_stubs.is_some() && fallback_modules.peek().is_some() {
        return Ok(found_stubs);
    } else if found_stubs.is_some() {
        return Err(FindError::no_source(module));
    }

    for module in fallback_modules {
        if let Some(module_result) = continue_find_module(module, rest)? {
            return Ok(Some(module_result));
        }
    }

    Ok(None)
}

fn find_module_prefixes<'a>(
    prefix: ModuleName,
    include: impl Iterator<Item = &'a PathBuf>,
) -> Vec<ModuleName> {
    let components = prefix.components();
    let first = &components[0];
    let rest = &components[1..];
    let mut results = Vec::new();
    if rest.is_empty() {
        results = find_one_part_prefix(first, include)
    } else {
        let mut current_result = find_one_part(first, include);
        for (i, part) in rest.iter().enumerate() {
            let is_last = i == rest.len() - 1;
            match current_result {
                None => {
                    break;
                }
                Some(
                    FindResult::SingleFilePyiModule(_)
                    | FindResult::SingleFilePyModule(_)
                    | FindResult::CompiledModule(_),
                ) => {
                    break;
                }
                Some(FindResult::RegularPackage(_, next_root)) => {
                    if is_last {
                        results = find_one_part_prefix(part, iter::once(&next_root));
                        break;
                    } else {
                        current_result = find_one_part(part, iter::once(&next_root));
                    }
                }
                Some(FindResult::NamespacePackage(next_roots)) => {
                    if is_last {
                        results = find_one_part_prefix(part, next_roots.iter());
                        break;
                    } else {
                        current_result = find_one_part(part, next_roots.iter());
                    }
                }
            }
        }
    }
    results.iter().map(|(_, name)| *name).collect::<Vec<_>>()
}

/// Get the given [`ModuleName`] from this config's search and site package paths.
/// We take the `path` of the file we're searching for the module from to determine if
/// we should replace imports with `typing.Any`.
/// Return `Err` when indicating the module could not be found.
pub fn find_import(
    config: &ConfigFile,
    module: ModuleName,
    path: Option<&Path>,
) -> Result<ModulePath, FindError> {
    if let Some(path) = config.custom_module_paths.get(&module) {
        Ok(path.clone())
    } else if module != ModuleName::builtins() && config.replace_imports_with_any(path, module) {
        Err(FindError::Ignored)
    } else if let Some(path) = find_module_in_search_path(module, config.search_path())? {
        Ok(path)
    } else if let Some(custom_typeshed_path) = &config.typeshed_path
        && let Some(path) = find_module_in_search_path(
            module,
            std::iter::once(&custom_typeshed_path.join("stdlib")),
        )?
    {
        Ok(path)
    } else if let Some(path) = typeshed()
        .map_err(|err| FindError::not_found(err, module))?
        .find(module)
    {
        Ok(path)
    } else if !config.disable_search_path_heuristics
        && let Some(path) = find_module_in_search_path(module, config.fallback_search_path.iter())?
    {
        Ok(path)
    } else if let Some(path) = find_module_in_site_package_path(
        module,
        config.site_package_path(),
        config.ignore_missing_source,
    )? {
        Ok(path)
    } else if config.ignore_missing_imports(path, module) {
        Err(FindError::Ignored)
    } else {
        Err(FindError::import_lookup_path(
            config.structured_import_lookup_path(),
            module,
            &config.source,
        ))
    }
}

/// Find all legitimate imports that start with `module`
pub fn find_import_prefixes(config: &ConfigFile, module: ModuleName) -> Vec<ModuleName> {
    let mut results = find_module_prefixes(
        module,
        config.search_path().chain(config.site_package_path()),
    );

    if let Ok(ts) = typeshed() {
        let module_str = module.as_str();
        let typeshed_modules = ts
            .modules()
            .filter(|m| module_str.is_empty() || m.as_str().starts_with(module_str));

        results.extend(typeshed_modules);
    }

    results
}

#[cfg(test)]
mod tests {
    use pyrefly_util::test_path::TestPath;

    use super::*;

    #[test]
    fn test_find_module_simple() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![TestPath::dir(
                "foo",
                vec![
                    TestPath::file("__init__.py"),
                    TestPath::file("bar.py"),
                    TestPath::file("baz.pyi"),
                ],
            )],
        );
        assert_eq!(
            find_module_in_search_path(
                ModuleName::from_str("foo.bar"),
                [root.to_path_buf()].iter(),
            )
            .unwrap(),
            Some(ModulePath::filesystem(root.join("foo/bar.py")))
        );
        assert_eq!(
            find_module_in_search_path(
                ModuleName::from_str("foo.baz"),
                [root.to_path_buf()].iter(),
            )
            .unwrap(),
            Some(ModulePath::filesystem(root.join("foo/baz.pyi")))
        );
        assert_eq!(
            find_module_in_search_path(
                ModuleName::from_str("foo.qux"),
                [root.to_path_buf()].iter(),
            )
            .unwrap(),
            None,
        );
    }

    #[test]
    fn test_find_module_init() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![TestPath::dir(
                "foo",
                vec![
                    TestPath::file("__init__.py"),
                    TestPath::dir("bar", vec![TestPath::file("__init__.py")]),
                    TestPath::dir("baz", vec![TestPath::file("__init__.pyi")]),
                ],
            )],
        );
        assert_eq!(
            find_module_in_search_path(
                ModuleName::from_str("foo.bar"),
                [root.to_path_buf()].iter(),
            )
            .unwrap(),
            Some(ModulePath::filesystem(root.join("foo/bar/__init__.py")))
        );
        assert_eq!(
            find_module_in_search_path(
                ModuleName::from_str("foo.baz"),
                [root.to_path_buf()].iter(),
            )
            .unwrap(),
            Some(ModulePath::filesystem(root.join("foo/baz/__init__.pyi")))
        );
    }

    #[test]
    fn test_find_pyi_takes_precedence() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![TestPath::dir(
                "foo",
                vec![
                    TestPath::file("__init__.py"),
                    TestPath::file("bar.pyi"),
                    TestPath::file("bar.py"),
                ],
            )],
        );
        assert_eq!(
            find_module_in_search_path(
                ModuleName::from_str("foo.bar"),
                [root.to_path_buf()].iter(),
            )
            .unwrap(),
            Some(ModulePath::filesystem(root.join("foo/bar.pyi")))
        );
    }

    #[test]
    fn test_find_init_takes_precedence() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![TestPath::dir(
                "foo",
                vec![
                    TestPath::file("__init__.py"),
                    TestPath::file("bar.py"),
                    TestPath::dir("bar", vec![TestPath::file("__init__.py")]),
                ],
            )],
        );
        assert_eq!(
            find_module_in_search_path(
                ModuleName::from_str("foo.bar"),
                [root.to_path_buf()].iter(),
            )
            .unwrap(),
            Some(ModulePath::filesystem(root.join("foo/bar/__init__.py")))
        );
    }

    #[test]
    fn test_basic_namespace_package() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![
                TestPath::dir("a", vec![]),
                TestPath::dir("b", vec![TestPath::dir("c", vec![])]),
                TestPath::dir("c", vec![TestPath::dir("d", vec![TestPath::file("e.py")])]),
            ],
        );
        let search_roots = [root.to_path_buf()];
        assert_eq!(
            find_module_in_search_path(ModuleName::from_str("a"), search_roots.iter()).unwrap(),
            Some(ModulePath::namespace(root.join("a")))
        );
        assert_eq!(
            find_module_in_search_path(ModuleName::from_str("b"), search_roots.iter()).unwrap(),
            Some(ModulePath::namespace(root.join("b")))
        );
        assert_eq!(
            find_module_in_search_path(ModuleName::from_str("c.d"), search_roots.iter()).unwrap(),
            Some(ModulePath::namespace(root.join("c/d")))
        );
        assert_eq!(
            find_module_in_search_path(ModuleName::from_str("c.d.e"), search_roots.iter()).unwrap(),
            Some(ModulePath::filesystem(root.join("c/d/e.py")))
        );
    }

    #[test]
    fn test_find_regular_package_early_return() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![
                TestPath::dir(
                    "search_root0",
                    vec![TestPath::dir(
                        "a",
                        vec![TestPath::file("__init__.py"), TestPath::file("b.py")],
                    )],
                ),
                TestPath::dir(
                    "search_root1",
                    vec![TestPath::dir(
                        "a",
                        vec![TestPath::file("__init__.py"), TestPath::file("c.py")],
                    )],
                ),
            ],
        );
        assert_eq!(
            find_module_in_search_path(
                ModuleName::from_str("a.c"),
                [root.join("search_root0"), root.join("search_root1")].iter(),
            )
            .unwrap(),
            // We won't find `a.c` because when searching for package `a`, we've already
            // committed to `search_root0/a/` as the path to search next for `c`. And there's
            // no `c.py` in `search_root0/a/`.
            None
        );
    }

    #[test]
    fn test_find_namespace_package_no_early_return() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![
                TestPath::dir(
                    "search_root0",
                    vec![TestPath::dir("a", vec![TestPath::file("b.py")])],
                ),
                TestPath::dir(
                    "search_root1",
                    vec![TestPath::dir("a", vec![TestPath::file("c.py")])],
                ),
            ],
        );
        assert_eq!(
            find_module_in_search_path(
                ModuleName::from_str("a.c"),
                [root.join("search_root0"), root.join("search_root1")].iter(),
            )
            .unwrap(),
            // We will find `a.c` because `a` is a namespace package whose search roots
            // include both `search_root0/a/` and `search_root1/a/`.
            Some(ModulePath::filesystem(root.join("search_root1/a/c.py")))
        );
    }

    #[test]
    fn test_find_site_package_path_no_py_typed() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![
                TestPath::dir(
                    "foo",
                    vec![
                        TestPath::file("__init__.py"),
                        TestPath::dir("bar", vec![TestPath::file("__init__.py")]),
                        TestPath::dir("baz", vec![TestPath::file("__init__.pyi")]),
                    ],
                ),
                TestPath::dir(
                    "foo-stubs",
                    vec![
                        TestPath::file("__init__.py"),
                        TestPath::dir("bar", vec![TestPath::file("__init__.py")]),
                    ],
                ),
            ],
        );
        assert_eq!(
            find_module_in_site_package_path(
                ModuleName::from_str("foo.bar"),
                [root.to_path_buf()].iter(),
                false,
            )
            .unwrap()
            .unwrap(),
            ModulePath::filesystem(root.join("foo-stubs/bar/__init__.py")),
        );
        assert_eq!(
            find_module_in_site_package_path(
                ModuleName::from_str("foo.baz"),
                [root.to_path_buf()].iter(),
                false,
            )
            .unwrap()
            .unwrap(),
            ModulePath::filesystem(root.join("foo/baz/__init__.pyi")),
        );
        assert!(
            find_module_in_site_package_path(
                ModuleName::from_str("foo.qux"),
                [root.to_path_buf()].iter(),
                false,
            )
            .unwrap()
            .is_none()
        );
    }

    #[test]
    fn test_find_site_package_path_no_stubs() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![TestPath::dir(
                "foo",
                vec![
                    TestPath::file("__init__.py"),
                    TestPath::dir("bar", vec![TestPath::file("__init__.py")]),
                    TestPath::dir("baz", vec![TestPath::file("__init__.pyi")]),
                ],
            )],
        );
        assert_eq!(
            find_module_in_site_package_path(
                ModuleName::from_str("foo.bar"),
                [root.to_path_buf()].iter(),
                false
            )
            .unwrap()
            .unwrap(),
            ModulePath::filesystem(root.join("foo/bar/__init__.py"))
        );
        assert_eq!(
            find_module_in_site_package_path(
                ModuleName::from_str("foo.baz"),
                [root.to_path_buf()].iter(),
                false,
            )
            .unwrap()
            .unwrap(),
            ModulePath::filesystem(root.join("foo/baz/__init__.pyi"))
        );
        assert!(matches!(
            find_module_in_site_package_path(
                ModuleName::from_str("foo.qux"),
                [root.to_path_buf()].iter(),
                false,
            ),
            Ok(None)
        ));
    }

    #[test]
    fn test_find_site_package_path_partial_py_typed() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![
                TestPath::dir(
                    "foo",
                    vec![
                        TestPath::file("__init__.py"),
                        TestPath::dir("bar", vec![TestPath::file("__init__.py")]),
                        TestPath::dir("baz", vec![TestPath::file("__init__.pyi")]),
                    ],
                ),
                TestPath::dir(
                    "foo-stubs",
                    vec![TestPath::file_with_contents("py.typed", "partial\n")],
                ),
            ],
        );
        assert_eq!(
            find_module_in_site_package_path(
                ModuleName::from_str("foo.bar"),
                [root.to_path_buf()].iter(),
                false,
            )
            .unwrap()
            .unwrap(),
            ModulePath::filesystem(root.join("foo/bar/__init__.py")),
        );
        assert_eq!(
            find_module_in_site_package_path(
                ModuleName::from_str("foo.baz"),
                [root.to_path_buf()].iter(),
                false,
            )
            .unwrap()
            .unwrap(),
            ModulePath::filesystem(root.join("foo/baz/__init__.pyi"))
        );
        assert!(
            find_module_in_site_package_path(
                ModuleName::from_str("foo.qux"),
                [root.to_path_buf()].iter(),
                false,
            )
            .unwrap()
            .is_none()
        );
    }

    #[test]
    fn test_find_site_package_path_no_stubs_with_py_typed() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![TestPath::dir(
                "foo",
                vec![
                    TestPath::file("py.typed"),
                    TestPath::file("__init__.py"),
                    TestPath::dir("bar", vec![TestPath::file("__init__.py")]),
                    TestPath::dir("baz", vec![TestPath::file("__init__.pyi")]),
                ],
            )],
        );
        assert_eq!(
            find_module_in_site_package_path(
                ModuleName::from_str("foo.bar"),
                [root.to_path_buf()].iter(),
                false,
            )
            .unwrap()
            .unwrap(),
            ModulePath::filesystem(root.join("foo/bar/__init__.py")),
        );
        assert_eq!(
            find_module_in_site_package_path(
                ModuleName::from_str("foo.baz"),
                [root.to_path_buf()].iter(),
                false,
            )
            .unwrap()
            .unwrap(),
            ModulePath::filesystem(root.join("foo/baz/__init__.pyi")),
        );
        assert!(
            find_module_in_site_package_path(
                ModuleName::from_str("foo.qux"),
                [root.to_path_buf()].iter(),
                false,
            )
            .unwrap()
            .is_none()
        );
    }

    #[test]
    fn test_find_site_package_path_no_source() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![
                TestPath::dir(
                    "foo-stubs",
                    vec![
                        TestPath::file("__init__.py"),
                        TestPath::dir("bar", vec![TestPath::file("__init__.py")]),
                    ],
                ),
                TestPath::dir("baz", vec![]),
                TestPath::dir(
                    "baz-stubs",
                    vec![
                        TestPath::file("__init__.py"),
                        TestPath::dir("qux", vec![TestPath::file("__init__.py")]),
                    ],
                ),
            ],
        );
        assert!(
            find_module_in_site_package_path(
                ModuleName::from_str("foo.bar"),
                [root.to_path_buf()].iter(),
                false,
            )
            .is_err()
        );
        assert_eq!(
            find_module_in_site_package_path(
                ModuleName::from_str("foo.bar"),
                [root.to_path_buf()].iter(),
                true,
            )
            .unwrap()
            .unwrap(),
            ModulePath::filesystem(root.join("foo-stubs/bar/__init__.py")),
        );
        assert_eq!(
            find_module_in_site_package_path(
                ModuleName::from_str("baz.qux"),
                [root.to_path_buf()].iter(),
                false,
            )
            .unwrap()
            .unwrap(),
            ModulePath::filesystem(root.join("baz-stubs/qux/__init__.py")),
        );
    }

    #[test]
    fn test_find_module_prefixes_file() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(root, vec![TestPath::file("foo.py")]);
        assert_eq!(
            find_module_prefixes(ModuleName::from_str("fo"), [root.to_path_buf()].iter(),),
            vec![ModuleName::from_str("foo")]
        );
    }
    #[test]
    fn test_find_module_prefixes_ignores_init() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![TestPath::file("foo.py"), TestPath::file("__init__.py")],
        );
        assert_eq!(
            find_module_prefixes(ModuleName::from_str(""), [root.to_path_buf()].iter(),),
            vec![ModuleName::from_str("foo")]
        );
    }
    #[test]
    fn test_find_module_prefixes_nested_file() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![TestPath::dir("baz", vec![TestPath::file("foo.py")])],
        );
        assert_eq!(
            find_module_prefixes(ModuleName::from_str("baz.fo"), [root.to_path_buf()].iter(),),
            vec![ModuleName::from_str("foo")]
        );
    }
    #[test]
    fn test_find_module_prefixes_nested_regular_package() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![TestPath::dir(
                "baz",
                vec![TestPath::dir("foo", vec![TestPath::file("__init__.py")])],
            )],
        );
        assert_eq!(
            find_module_prefixes(ModuleName::from_str("baz.fo"), [root.to_path_buf()].iter(),),
            vec![ModuleName::from_str("foo")]
        );
    }
    #[test]
    fn test_find_module_prefixes_regular_package() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![TestPath::dir("foo", vec![TestPath::file("__init__.py")])],
        );
        assert_eq!(
            find_module_prefixes(ModuleName::from_str("fo"), [root.to_path_buf()].iter(),),
            vec![ModuleName::from_str("foo")]
        );
    }
    #[test]
    fn test_find_module_prefixes_multiple_search_paths() {
        let root = tempfile::tempdir().unwrap();
        let root2 = tempfile::tempdir().unwrap();
        TestPath::setup_test_directory(
            root.path(),
            vec![TestPath::dir("foo", vec![TestPath::file("__init__.py")])],
        );
        TestPath::setup_test_directory(root2.path(), vec![TestPath::file("foo2.py")]);
        assert_eq!(
            find_module_prefixes(
                ModuleName::from_str("fo"),
                [root.path().to_path_buf(), root2.path().to_path_buf()].iter(),
            ),
            vec![ModuleName::from_str("foo"), ModuleName::from_str("foo2")]
        );
    }

    #[test]
    fn test_find_module_prefixes_nested_namespaces() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![
                TestPath::dir("foo", Vec::new()),
                TestPath::dir("foo2", Vec::new()),
            ],
        );
        let mut res = find_module_prefixes(ModuleName::from_str("fo"), [root.to_path_buf()].iter());
        res.sort();
        assert_eq!(
            res,
            vec![ModuleName::from_str("foo"), ModuleName::from_str("foo2")]
        );
    }

    #[test]
    fn test_find_module_prefixes_namespaces() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![
                TestPath::dir("foo", Vec::new()),
                TestPath::dir("foo2", Vec::new()),
            ],
        );
        let mut res = find_module_prefixes(ModuleName::from_str("fo"), [root.to_path_buf()].iter());
        res.sort();
        assert_eq!(
            res,
            vec![ModuleName::from_str("foo"), ModuleName::from_str("foo2")]
        );
    }

    #[test]
    fn test_find_compiled_module() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(root, vec![TestPath::file("compiled_module.pyc")]);
        let find_compiled_result = find_module_in_search_path(
            ModuleName::from_str("compiled_module"),
            [root.to_path_buf()].iter(),
        );
        assert!(matches!(find_compiled_result, Err(FindError::Ignored)));
        assert_eq!(
            find_module_in_search_path(
                ModuleName::from_str("compiled_module.nested"),
                [root.to_path_buf()].iter(),
            )
            .unwrap(),
            None
        );
    }

    #[test]
    fn test_find_compiled_module_with_source() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![TestPath::file("foo.py"), TestPath::file("foo.pyc")],
        );
        // Ensure that the source file takes precedence over the compiled file
        assert_eq!(
            find_module_in_search_path(ModuleName::from_str("foo"), [root.to_path_buf()].iter(),)
                .unwrap(),
            Some(ModulePath::filesystem(root.join("foo.py")))
        );
    }

    #[test]
    fn test_nested_imports_with_compiled_modules() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![TestPath::dir(
                "subdir",
                vec![
                    TestPath::file("another_compiled_module.pyc"),
                    TestPath::file("nested_import.py"),
                ],
            )],
        );
        assert_eq!(
            find_module_in_search_path(
                ModuleName::from_str("subdir.nested_import"),
                [root.to_path_buf()].iter(),
            )
            .unwrap(),
            Some(ModulePath::filesystem(root.join("subdir/nested_import.py")))
        );
        let find_compiled_result = find_module_in_search_path(
            ModuleName::from_str("subdir.another_compiled_module"),
            [root.to_path_buf()].iter(),
        );
        assert!(matches!(find_compiled_result, Err(FindError::Ignored)));
    }

    #[test]
    fn test_find_one_part_with_pyc() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![
                TestPath::file("nested_module.pyc"),
                TestPath::file("another_nested_module.py"),
                TestPath::file("cython_module.pyx"),
                TestPath::file("windows_dll.pyd"),
            ],
        );
        let result = find_one_part(&Name::new("nested_module"), [root.to_path_buf()].iter());
        assert_eq!(
            result,
            Some(FindResult::CompiledModule(root.join("nested_module.pyc")))
        );
        let result = find_one_part(&Name::new("cython_module"), [root.to_path_buf()].iter());
        assert_eq!(
            result,
            Some(FindResult::CompiledModule(root.join("cython_module.pyx")))
        );
        let result = find_one_part(&Name::new("windows_dll"), [root.to_path_buf()].iter());
        assert_eq!(
            result,
            Some(FindResult::CompiledModule(root.join("windows_dll.pyd")))
        );
        let result = find_one_part(
            &Name::new("another_nested_module"),
            [root.to_path_buf()].iter(),
        );
        assert_eq!(
            result,
            Some(FindResult::SingleFilePyModule(
                root.join("another_nested_module.py")
            ))
        );
    }

    #[test]
    fn test_continue_find_module_with_pyc() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(
            root,
            vec![TestPath::dir(
                "subdir",
                vec![
                    TestPath::file("nested_module.pyc"),
                    TestPath::file("another_nested_module.py"),
                ],
            )],
        );
        let start_result =
            find_one_part(&Name::new("subdir"), [root.to_path_buf()].iter()).unwrap();
        let module_path = continue_find_module(start_result, &[Name::new("nested_module")]);
        assert!(matches!(module_path, Err(FindError::Ignored)));
        let start_result =
            find_one_part(&Name::new("subdir"), [root.to_path_buf()].iter()).unwrap();
        let module_path =
            continue_find_module(start_result, &[Name::new("another_nested_module")]).unwrap();
        assert_eq!(
            module_path,
            Some(ModulePath::filesystem(
                root.join("subdir/another_nested_module.py")
            ))
        );
    }

    #[test]
    fn test_continue_find_module_signature() {
        let start_result =
            FindResult::RegularPackage(PathBuf::from("path/to/init.py"), PathBuf::from("path/to"));
        let components_rest = vec![Name::new("test_module")];
        let result: Result<Option<ModulePath>, FindError> =
            continue_find_module(start_result, &components_rest);
        let unwrapped_result = result.unwrap();
        assert_eq!(unwrapped_result, None);
    }

    #[test]
    fn test_continue_find_module_with_pyc_no_source_ignored() {
        let tempdir = tempfile::tempdir().unwrap();
        let root = tempdir.path();
        TestPath::setup_test_directory(root, vec![TestPath::file("module.pyc")]);
        let start_result =
            find_one_part(&Name::new("module"), [root.to_path_buf()].iter()).unwrap();
        let result = continue_find_module(start_result, &[]);
        assert!(matches!(result, Err(FindError::Ignored)));
    }
}
