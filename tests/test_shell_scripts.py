import unittest
from pathlib import Path


class ShellScriptPortabilityTests(unittest.TestCase):
    def test_shell_scripts_use_lf_line_endings(self) -> None:
        root = Path(__file__).resolve().parents[1]
        scripts = sorted((root / "scripts").glob("*.sh"))

        self.assertTrue(scripts)
        offenders = [path.relative_to(root).as_posix() for path in scripts if b"\r\n" in path.read_bytes()]
        self.assertEqual(offenders, [], f"CRLF breaks Linux shebang execution: {offenders}")


if __name__ == "__main__":
    unittest.main()
