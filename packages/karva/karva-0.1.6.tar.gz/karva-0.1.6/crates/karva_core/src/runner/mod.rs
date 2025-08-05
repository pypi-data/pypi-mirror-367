use karva_project::Project;
#[cfg(test)]
use karva_project::testing::TestEnv;

use crate::{
    collection::TestCaseCollector,
    diagnostic::reporter::{DummyReporter, Reporter},
    discovery::StandardDiscoverer,
    utils::with_gil,
};

mod diagnostic;

pub(crate) use diagnostic::RunDiagnostics;

pub trait TestRunner {
    fn test(&self) -> RunDiagnostics {
        self.test_with_reporter(&mut DummyReporter)
    }
    fn test_with_reporter(&self, reporter: &mut dyn Reporter) -> RunDiagnostics;
}

pub(crate) struct StandardTestRunner<'proj> {
    project: &'proj Project,
}

impl<'proj> StandardTestRunner<'proj> {
    #[must_use]
    pub(crate) const fn new(project: &'proj Project) -> Self {
        Self { project }
    }

    fn test_impl(&self, reporter: &mut dyn Reporter) -> RunDiagnostics {
        with_gil(self.project, |py| {
            let (session, discovery_diagnostics) =
                StandardDiscoverer::new(self.project).discover(py);

            let collected_session = TestCaseCollector::collect(py, &session);

            let total_test_cases = collected_session.total_test_cases();

            let total_modules = collected_session.total_modules();

            tracing::info!(
                "Collected {} test{} in {} module{}",
                total_test_cases,
                if total_test_cases == 1 { "" } else { "s" },
                total_modules,
                if total_modules == 1 { "" } else { "s" },
            );

            let mut diagnostics = RunDiagnostics::default();

            diagnostics.add_diagnostics(discovery_diagnostics);

            reporter.set(total_test_cases);

            diagnostics.update(&collected_session.run_with_reporter(py, reporter));

            diagnostics
        })
    }
}

impl TestRunner for StandardTestRunner<'_> {
    fn test_with_reporter(&self, reporter: &mut dyn Reporter) -> RunDiagnostics {
        self.test_impl(reporter)
    }
}

impl TestRunner for Project {
    fn test_with_reporter(&self, reporter: &mut dyn Reporter) -> RunDiagnostics {
        let test_runner = StandardTestRunner::new(self);
        test_runner.test_with_reporter(reporter)
    }
}

#[cfg(test)]
impl TestRunner for TestEnv {
    fn test_with_reporter(&self, reporter: &mut dyn Reporter) -> RunDiagnostics {
        let project = Project::new(self.cwd(), vec![self.cwd()]);
        let test_runner = StandardTestRunner::new(&project);
        test_runner.test_with_reporter(reporter)
    }
}

#[cfg(test)]
mod tests {
    use karva_project::{path::SystemPathBuf, testing::TestEnv, utils::module_name};
    use rstest::rstest;

    use super::*;
    use crate::{
        diagnostic::{Diagnostic, DiagnosticSeverity},
        runner::diagnostic::DiagnosticStats,
    };

    #[test]
    fn test_fixture_manager_add_fixtures_impl_three_dependencies_different_scopes_with_fixture_in_function()
     {
        let env = TestEnv::with_files([
            (
                "<test>/conftest.py",
                r"
import karva
@karva.fixture(scope='function')
def x():
    return 1

@karva.fixture(scope='function')
def y(x):
    return 1

@karva.fixture(scope='function')
def z(x, y):
    return 1
            ",
            ),
            ("<test>/inner/test_file.py", "def test_1(z): pass"),
        ]);

        let result = env.test();

        assert!(result.passed(), "{result:?}");
    }

    #[test]
    fn test_runner_given_nested_path() {
        let env = TestEnv::with_files([
            (
                "<test>/conftest.py",
                r"
import karva
@karva.fixture(scope='module')
def x():
    return 1
            ",
            ),
            ("<test>/test_file.py", "def test_1(x): pass"),
        ]);

        let result = env.test();

        assert!(result.passed(), "{result:?}");
    }

    #[test]
    fn test_parametrize_with_fixture() {
        let env = TestEnv::with_file(
            "<test>/test_file.py",
            r#"
import karva

@karva.fixture
def fixture_value():
    return 42

@karva.tags.parametrize("a", [1, 2, 3])
def test_parametrize_with_fixture(a, fixture_value):
    assert a > 0
    assert fixture_value == 42"#,
        );

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();

        for _ in 0..3 {
            expected_stats.add_passed();
        }

        assert_eq!(*result.stats(), expected_stats, "{result:?}");
    }

    #[test]
    fn test_parametrize_with_fixture_parametrize_priority() {
        let env = TestEnv::with_file(
            "<test>/test_file.py",
            r#"import karva

@karva.fixture
def a():
    return -1

@karva.tags.parametrize("a", [1, 2, 3])
def test_parametrize_with_fixture(a):
    assert a > 0"#,
        );

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();

        for _ in 0..3 {
            expected_stats.add_passed();
        }

        assert_eq!(*result.stats(), expected_stats, "{result:?}");
    }

    #[test]
    fn test_parametrize_two_decorators() {
        let env = TestEnv::with_file(
            "<test>/test_file.py",
            r#"import karva

@karva.tags.parametrize("a", [1, 2])
@karva.tags.parametrize("b", [1, 2])
def test_function(a: int, b: int):
    assert a > 0 and b > 0
"#,
        );

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();

        for _ in 0..4 {
            expected_stats.add_passed();
        }

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_parametrize_three_decorators() {
        let env = TestEnv::with_file(
            "<test>/test_file.py",
            r#"
import karva

@karva.tags.parametrize("a", [1, 2])
@karva.tags.parametrize("b", [1, 2])
@karva.tags.parametrize("c", [1, 2])
def test_function(a: int, b: int, c: int):
    assert a > 0 and b > 0 and c > 0
"#,
        );

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();

        for _ in 0..8 {
            expected_stats.add_passed();
        }

        assert_eq!(*result.stats(), expected_stats, "{result:?}");
    }

    #[test]
    fn test_fixture_generator() {
        let env = TestEnv::with_file(
            "<test>/test_file.py",
            r"
import karva

@karva.fixture
def fixture_generator():
    yield 1

def test_fixture_generator(fixture_generator):
    assert fixture_generator == 1
",
        );

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();

        expected_stats.add_passed();

        assert_eq!(*result.stats(), expected_stats, "{result:?}");
    }

    #[test]
    fn test_fixture_generator_two_yields() {
        let env = TestEnv::with_file(
            "<test>/test_file.py",
            r"import karva

@karva.fixture
def fixture_generator():
    yield 1
    yield 2

def test_fixture_generator(fixture_generator):
    assert fixture_generator == 1
",
        );

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();

        expected_stats.add_passed();

        let module_name_path = env.mapped_path("<test>").unwrap().join("test_file.py");
        let module_name = module_name(&env.cwd(), &module_name_path).unwrap();

        assert_eq!(*result.stats(), expected_stats, "{result:?}");

        assert_eq!(result.diagnostics().len(), 1);
        let first_diagnostic = &result.diagnostics()[0];
        let expected_diagnostic = Diagnostic::warning(
            "fixture-error",
            Some(format!(
                "Fixture {module_name}::fixture_generator had more than one yield statement"
            )),
            None,
        );

        assert_eq!(*first_diagnostic, expected_diagnostic);
    }

    #[test]
    fn test_fixture_generator_fail_in_teardown() {
        let env = TestEnv::with_file(
            "<test>/test_file.py",
            r#"import karva

@karva.fixture
def fixture_generator():
    yield 1
    raise ValueError("fixture-error")

def test_fixture_generator(fixture_generator):
    assert fixture_generator == 1
"#,
        );

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();

        expected_stats.add_passed();

        let module_name_path = env.mapped_path("<test>").unwrap().join("test_file.py");
        let module_name = module_name(&env.cwd(), &module_name_path).unwrap();

        assert_eq!(*result.stats(), expected_stats, "{result:?}");

        assert_eq!(result.diagnostics().len(), 1);
        let first_diagnostic = &result.diagnostics()[0];
        assert_eq!(
            first_diagnostic.inner().message(),
            Some(format!("Failed to reset fixture {module_name}::fixture_generator").as_str()),
        );
        assert_eq!(
            first_diagnostic.severity(),
            &DiagnosticSeverity::Warning("fixture-error".to_string())
        );
    }

    #[test]
    fn test_fixture_with_name_parameter() {
        let env = TestEnv::with_file(
            "<test>/test_file.py",
            r#"import karva

@karva.fixture(name="fixture_name")
def fixture_1():
    return 1

def test_fixture_with_name_parameter(fixture_name):
    assert fixture_name == 1
"#,
        );

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();

        expected_stats.add_passed();

        assert_eq!(*result.stats(), expected_stats, "{result:?}");
    }

    #[test]
    fn test_fixture_is_different_in_different_functions() {
        let env = TestEnv::with_file(
            "<test>/test_file.py",
            r"import karva

class TestEnv:
    def __init__(self):
        self.x = 1

@karva.fixture
def fixture():
    return TestEnv()

def test_fixture(fixture):
    assert fixture.x == 1
    fixture.x = 2

def test_fixture_2(fixture):
    assert fixture.x == 1
    fixture.x = 2
",
        );

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();

        for _ in 0..2 {
            expected_stats.add_passed();
        }

        assert_eq!(*result.stats(), expected_stats, "{result:?}");
    }

    #[test]
    fn test_single_function() {
        let env = TestEnv::with_files([(
            "<test>/test_file.py",
            r"
            def test_1(): pass
            def test_2(): pass",
        )]);

        let mapped_path = env.mapped_path("<test>").unwrap().clone();

        let test_file1_path = mapped_path.join("test_file.py");

        let project = Project::new(
            env.cwd(),
            vec![SystemPathBuf::from(format!(
                "{}::test_1",
                test_file1_path.display()
            ))],
        );

        let test_runner = StandardTestRunner::new(&project);

        let result = test_runner.test();

        let mut expected_stats = DiagnosticStats::default();

        expected_stats.add_passed();

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_single_function_shadowed_by_file() {
        let env = TestEnv::with_files([(
            "<test>/test_file.py",
            r"
            def test_1(): pass
            def test_2(): pass",
        )]);

        let mapped_path = env.mapped_path("<test>").unwrap().clone();

        let test_file1_path = mapped_path.join("test_file.py");

        let project = Project::new(
            env.cwd(),
            vec![
                SystemPathBuf::from(format!("{}::test_1", test_file1_path.display())),
                test_file1_path,
            ],
        );

        let test_runner = StandardTestRunner::new(&project);

        let result = test_runner.test();

        let mut expected_stats = DiagnosticStats::default();

        for _ in 0..2 {
            expected_stats.add_passed();
        }

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_single_function_shadowed_by_directory() {
        let env = TestEnv::with_files([(
            "<test>/test_file.py",
            r"
            def test_1(): pass
            def test_2(): pass",
        )]);

        let mapped_path = env.mapped_path("<test>").unwrap().clone();

        let test_file1_path = mapped_path.join("test_file.py");

        let project = Project::new(
            env.cwd(),
            vec![
                SystemPathBuf::from(format!("{}::test_1", test_file1_path.display())),
                mapped_path,
            ],
        );

        let test_runner = StandardTestRunner::new(&project);

        let result = test_runner.test();

        let mut expected_stats = DiagnosticStats::default();

        for _ in 0..2 {
            expected_stats.add_passed();
        }

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_fixture_from_current_package_session_scope() {
        let env = TestEnv::with_files([
            (
                "<test>/tests/conftest.py",
                r"
import karva
@karva.fixture(scope='session')
def x():
    return 1
            ",
            ),
            ("<test>/tests/test_file.py", "def test_1(x): pass"),
        ]);

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();

        expected_stats.add_passed();

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_fixture_from_current_package_function_scope() {
        let env = TestEnv::with_files([
            (
                "<test>/tests/conftest.py",
                r"
import karva
@karva.fixture
def x():
    return 1
            ",
            ),
            ("<test>/tests/test_file.py", "def test_1(x): pass"),
        ]);

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();

        expected_stats.add_passed();

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_finalizer_from_current_package_session_scope() {
        let env = TestEnv::with_files([
            (
                "<test>/tests/conftest.py",
                r"
import karva

arr = []

@karva.fixture(scope='session')
def x():
    yield 1
    arr.append(1)
            ",
            ),
            (
                "<test>/tests/test_file.py",
                r"
from .conftest import arr

def test_1(x):
    assert len(arr) == 0

def test_2(x):
    assert len(arr) == 0
",
            ),
        ]);

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();
        for _ in 0..2 {
            expected_stats.add_passed();
        }

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_finalizer_from_current_package_function_scope() {
        let env = TestEnv::with_files([
            (
                "<test>/tests/conftest.py",
                r"
import karva

arr = []

@karva.fixture
def x():
    yield 1
    arr.append(1)
            ",
            ),
            (
                "<test>/tests/test_file.py",
                r"
from .conftest import arr

def test_1(x):
    assert len(arr) == 0

def test_2(x):
    assert len(arr) == 1
",
            ),
        ]);

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();
        for _ in 0..2 {
            expected_stats.add_passed();
        }

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_discover_pytest_fixture() {
        let env = TestEnv::with_files([
            (
                "<test>/tests/conftest.py",
                r"
import pytest

@pytest.fixture
def x():
    return 1
",
            ),
            ("<test>/tests/test_1.py", "def test_1(x): pass"),
        ]);

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();

        expected_stats.add_passed();

        assert_eq!(*result.stats(), expected_stats);
    }

    #[rstest]
    #[case("pytest")]
    #[case("karva")]
    fn test_dynamic_fixture_scope_session_scope(#[case] framework: &str) {
        let env = TestEnv::with_file(
            "<test>/test_dynamic_scope.py",
            &format!(
                r#"
from {framework} import fixture

def dynamic_scope(fixture_name, config):
    if fixture_name.endswith("_session"):
        return "session"
    return "function"

@fixture(scope=dynamic_scope)
def x_session():
    return []

def test_1(x_session):
    x_session.append(1)
    assert x_session == [1]

def test_2(x_session):
    x_session.append(2)
    assert x_session == [1, 2]
    "#,
            ),
        );

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();

        for _ in 0..2 {
            expected_stats.add_passed();
        }

        assert_eq!(*result.stats(), expected_stats);
    }

    #[rstest]
    #[case("pytest")]
    #[case("karva")]
    fn test_dynamic_fixture_scope_function_scope(#[case] framework: &str) {
        let env = TestEnv::with_file(
            "<test>/test_dynamic_scope.py",
            &format!(
                r#"
from {framework} import fixture

def dynamic_scope(fixture_name, config):
    if fixture_name.endswith("_function"):
        return "function"
    return "function"

@fixture(scope=dynamic_scope)
def x_function():
    return []

def test_1(x_function):
    x_function.append(1)
    assert x_function == [1]

def test_2(x_function):
    x_function.append(2)
    assert x_function == [2]
    "#,
            ),
        );

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();

        for _ in 0..2 {
            expected_stats.add_passed();
        }

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_use_fixtures_single_fixture() {
        let env = TestEnv::with_file(
            "<test>/test_use_fixtures.py",
            r#"
import karva

arr = []

@karva.fixture
def setup_fixture():
    arr.append(1)

@karva.tags.use_fixtures("setup_fixture")
def test_with_use_fixture():
    assert arr == [1]
"#,
        );

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();

        expected_stats.add_passed();

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_use_fixtures_multiple_fixtures() {
        let env = TestEnv::with_file(
            "<test>/test_use_fixtures.py",
            r#"
import karva

arr = []

@karva.fixture
def fixture1():
    arr.append(1)

@karva.fixture
def fixture2():
    arr.append(2)

@karva.tags.use_fixtures("fixture1", "fixture2")
def test_with_multiple_use_fixtures():
    assert arr == [1, 2]
"#,
        );

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();
        expected_stats.add_passed();

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_use_fixtures_combined_with_parameter_fixtures() {
        let env = TestEnv::with_file(
            "<test>/test_use_fixtures.py",
            r#"
import karva

@karva.fixture
def setup_fixture():
    return "setup_value"

@karva.fixture
def param_fixture():
    return "param_value"

@karva.tags.use_fixtures("setup_fixture")
def test_combined_fixtures(param_fixture):
    # Both setup_fixture (from use_fixtures) and param_fixture (from parameters) should be resolved
    assert True
"#,
        );

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();
        expected_stats.add_passed();

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_use_fixtures_with_parametrize() {
        let env = TestEnv::with_file(
            "<test>/test_use_fixtures.py",
            r#"
import karva

arr = []

@karva.fixture
def setup_fixture():
    arr.append(1)

@karva.tags.use_fixtures("setup_fixture")
@karva.tags.parametrize("value", [1, 2, 3])
def test_use_fixtures_with_parametrize(value):
    assert value > 0
    # Fixtures are called before any run
    assert arr == [1, 1, 1]
"#,
        );

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();
        for _ in 0..3 {
            expected_stats.add_passed();
        }

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_use_fixtures_multiple_decorators() {
        let env = TestEnv::with_file(
            "<test>/test_use_fixtures.py",
            r#"
import karva

arr = []

@karva.fixture
def fixture1():
    arr.append(1)

@karva.fixture
def fixture2():
    arr.append(2)

@karva.tags.use_fixtures("fixture1")
@karva.tags.use_fixtures("fixture2")
def test_multiple_use_fixtures_decorators():
    assert arr == [1, 2]
"#,
        );

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();
        expected_stats.add_passed();

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_use_fixtures_fixture_not_found_but_not_used() {
        let env = TestEnv::with_file(
            "<test>/test_use_fixtures.py",
            r#"
import karva

@karva.tags.use_fixtures("nonexistent_fixture")
def test_missing_fixture():
    assert True
"#,
        );

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();

        expected_stats.add_passed();

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_use_fixtures_generator_fixture() {
        let env = TestEnv::with_file(
            "<test>/test_use_fixtures.py",
            r#"
import karva

arr = []

@karva.fixture
def generator_fixture():
    arr.append(1)
    yield 1

@karva.tags.use_fixtures("generator_fixture")
def test_use_fixtures_with_generator():
    assert arr == [1]
"#,
        );

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();
        expected_stats.add_passed();

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_use_fixtures_session_scope() {
        let env = TestEnv::with_files([(
            "<test>/test_use_fixtures.py",
            r#"
import karva

arr = []

@karva.fixture(scope='session')
def session_fixture():
    arr.append(1)

@karva.tags.use_fixtures("session_fixture")
def test_session_1():
    assert arr == [1]

@karva.tags.use_fixtures("session_fixture")
def test_session_2():
    assert arr == [1]
"#,
        )]);

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();
        for _ in 0..2 {
            expected_stats.add_passed();
        }

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_use_fixtures_mixed_with_normal_fixtures() {
        let env = TestEnv::with_files([
            (
                "<test>/conftest.py",
                r#"
import karva

@karva.fixture
def shared_fixture():
    return "shared_value"

@karva.fixture
def use_fixture_only():
    return "use_only_value"
"#,
            ),
            (
                "<test>/test_use_fixtures.py",
                r#"
import karva

@karva.tags.use_fixtures("use_fixture_only")
def test_mixed_fixtures(shared_fixture):
    assert shared_fixture == "shared_value"
"#,
            ),
        ]);

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();

        expected_stats.add_passed();

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_pytest_mark_usefixtures_single_fixture() {
        let env = TestEnv::with_file(
            "<test>/test_pytest_use_fixtures.py",
            r#"
import pytest

arr = []

@pytest.fixture
def setup_fixture():
    arr.append(1)

@pytest.mark.usefixtures("setup_fixture")
def test_with_pytest_use_fixture():
    assert arr == [1]
"#,
        );

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();

        expected_stats.add_passed();

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_pytest_mark_usefixtures_multiple_fixtures() {
        let env = TestEnv::with_file(
            "<test>/test_pytest_use_fixtures.py",
            r#"
import pytest

arr = []

@pytest.fixture
def fixture1():
    arr.append(1)

@pytest.fixture
def fixture2():
    arr.append(2)

@pytest.mark.usefixtures("fixture1", "fixture2")
def test_with_multiple_pytest_use_fixtures():
    assert arr == [1, 2]
"#,
        );

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();
        expected_stats.add_passed();

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_pytest_mark_usefixtures_with_parametrize() {
        let env = TestEnv::with_file(
            "<test>/test_pytest_use_fixtures.py",
            r#"
import pytest

arr = []

@pytest.fixture
def setup_fixture():
    arr.append(1)

@pytest.mark.usefixtures("setup_fixture")
@pytest.mark.parametrize("value", [1, 2, 3])
def test_pytest_use_fixtures_with_parametrize(value):
    assert value > 0
    # Fixtures are called before any run
    assert arr == [1, 1, 1]
"#,
        );

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();
        for _ in 0..3 {
            expected_stats.add_passed();
        }

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_pytest_mark_usefixtures_session_scope() {
        let env = TestEnv::with_files([(
            "<test>/test_pytest_use_fixtures.py",
            r#"
import pytest

arr = []

@pytest.fixture(scope='session')
def session_fixture():
    arr.append(1)

@pytest.mark.usefixtures("session_fixture")
def test_pytest_session_1():
    assert arr == [1]

@pytest.mark.usefixtures("session_fixture")
def test_pytest_session_2():
    assert arr == [1]
"#,
        )]);

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();
        for _ in 0..2 {
            expected_stats.add_passed();
        }

        assert_eq!(*result.stats(), expected_stats);
    }

    #[test]
    fn test_fixture_override_in_test_modules() {
        let env = TestEnv::with_files([
            (
                "<test>/tests/conftest.py",
                r"
import karva

@karva.fixture
def username():
    return 'username'
",
            ),
            (
                "<test>/tests/test_something.py",
                r"
import karva

@karva.fixture
def username(username):
    return 'overridden-' + username

def test_username(username):
    assert username == 'overridden-username'
",
            ),
            (
                "<test>/tests/test_something_else.py",
                r"
import karva

@karva.fixture
def username(username):
    return 'overridden-else-' + username

def test_username(username):
    assert username == 'overridden-else-username'
",
            ),
        ]);

        let result = env.test();

        let mut expected_stats = DiagnosticStats::default();

        for _ in 0..2 {
            expected_stats.add_passed();
        }

        assert_eq!(*result.stats(), expected_stats);
    }
}
