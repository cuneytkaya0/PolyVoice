import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SETUP = (ROOT / "setup.bat").read_text(encoding="utf-8")
START = (ROOT / "start.bat").read_text(encoding="utf-8")
REQUIREMENTS = (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
GITIGNORE = (ROOT / ".gitignore").read_text(encoding="utf-8")


class InstallScriptTests(unittest.TestCase):
    def test_scripts_resolve_project_root_and_use_venv_python(self):
        for script in (SETUP, START):
            with self.subTest(script="setup" if script is SETUP else "start"):
                self.assertIn('set "PV_ROOT=%~dp0"', script)
                self.assertIn('cd /d "%PV_ROOT%"', script)
                self.assertIn('set "PV_PYTHON=%PV_ROOT%.venv\\Scripts\\python.exe"', script)
                self.assertIn('set "PYTHONHOME="', script)
                self.assertIn('set "PYTHONPATH="', script)
                self.assertIn('set "PYTHONNOUSERSITE=1"', script)

    def test_requirements_do_not_require_git_and_source_archives_are_commit_pinned(self):
        active = [line.strip() for line in REQUIREMENTS if line.strip() and not line.lstrip().startswith("#")]
        self.assertFalse(any("git+" in line.lower() for line in active))
        self.assertTrue(any("kokoro/archive/b96fef95e6a746495f92443fac7c688f90fc57fc.zip" in line for line in active))
        self.assertTrue(any("misaki/archive/9cda9268309160120fffee216280a9ca83ac4644.zip" in line for line in active))
        self.assertIn("phonemizer-fork==3.3.2", active)
        self.assertIn("espeakng-loader==0.2.4", active)

    def test_setup_validates_platform_environment_dependencies_and_real_speech(self):
        self.assertIn('if /i not "%PROCESSOR_ARCHITECTURE%"=="AMD64"', SETUP)
        self.assertIn('ver | findstr /c:"10.0."', SETUP)
        self.assertIn("scripts\\environment_check.py", SETUP)
        self.assertIn("scripts\\dependency_check.py", SETUP)
        self.assertIn("scripts\\smoke_test.py", SETUP)
        self.assertIn("Get-FileHash", SETUP)
        self.assertIn("bb701bd35b586c45966654ea2703c9bd116a6a4fc0a8ca755bd644c2c41c5ebe", SETUP)
        self.assertIn("if errorlevel 1 goto :functional_test_failed", SETUP)
        self.assertIn("PolyVoice setup completed. CPU TTS, local voices, and WAV previews passed", SETUP)
        self.assertNotIn("setx ", SETUP.lower())
        self.assertNotIn("ExecutionPolicy Bypass", SETUP)

    def test_start_checks_environment_then_dependencies_then_launches(self):
        env_check = START.index("stage=python-version started_local=")
        dependency_check = START.index("stage=dependency-check started_local=")
        run_app = START.index("stage=application started_local=")
        self.assertLess(env_check, dependency_check)
        self.assertLess(dependency_check, run_app)
        self.assertIn('"%PV_PYTHON%" "%PV_ROOT%scripts\\environment_check.py" --project-root "%PV_ROOT%." --venv', START)
        self.assertIn('"%PV_PYTHON%" "%PV_ROOT%scripts\\dependency_check.py"', START)
        self.assertIn('"%PV_PYTHON%" "%PV_ROOT%run.py" 2>>"%PV_DIAG_LOG%"', START)
        self.assertIn("stage=python-version exit_code=%PV_STAGE_EXIT%", START)
        self.assertIn("stage=dependency-check exit_code=%PV_STAGE_EXIT%", START)
        self.assertIn("stage=application exit_code=%PV_STAGE_EXIT%", START)
        self.assertIn('if "%PV_STAGE_EXIT%"=="-1073741510" goto :normal_shutdown', START)
        self.assertIn("Run setup.bat from the PolyVoice folder", START)

    def test_diagnostics_stay_local_rotated_and_bounded(self):
        self.assertIn("%PV_ROOT%.tmp\\diagnostics", START)
        self.assertIn('dir /b /a-d /o-d "%PV_DIAG_DIR%\\*.log"', START)
        self.assertIn('"skip=19 delims="', START)
        self.assertIn("262144", START)
        self.assertNotIn("GetEnvironmentVariables", START)
        self.assertIn(".tmp/", GITIGNORE)
        self.assertIn(".tools/", GITIGNORE)
        self.assertIn(".venv/", GITIGNORE)
        self.assertIn(".python/", GITIGNORE)
        self.assertIn("models/", GITIGNORE)
        self.assertIn("*.wav", GITIGNORE)

    def test_dependency_checker_fails_when_run_without_project_packages(self):
        result = subprocess.run(
            [sys.executable, "-S", str(ROOT / "scripts" / "dependency_check.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ERROR:", result.stderr)


if __name__ == "__main__":
    unittest.main()
