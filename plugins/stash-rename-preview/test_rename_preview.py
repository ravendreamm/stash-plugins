import unittest

from rename_preview import preview


class RenamePreviewTest(unittest.TestCase):
    def test_scene_with_optional_fields(self):
        result = preview("/data/scenes", "$studio_name$/$date$ - $title$",
                         "$studio_name$.{ $performers_female$ }$title${.$quality$}",
                         {"studio_name": "Studio", "date": "2026-01-02", "title": "Title",
                          "performers_female": "Person", "quality": "1080p"}, ".mp4")
        self.assertEqual(result, "/data/scenes/Studio/2026-01-02 - Title/Studio. Person Title.1080p.mp4")

    def test_optional_blocks_are_independent(self):
        result = preview("/data/scenes", "$studio_name$", "$title${.$quality$}{-$release_group$}",
                         {"studio_name": "Studio", "title": "Title", "release_group": "Group"}, ".mkv")
        self.assertEqual(result, "/data/scenes/Studio/Title-Group.mkv")

    def test_unsafe_metadata_cannot_add_directories(self):
        result = preview("/data/scenes", "$studio_name$", "$title$",
                         {"studio_name": "Studio/Other:Name", "title": "Title/Part"}, ".mp4")
        self.assertEqual(result, "/data/scenes/StudioOtherName/TitlePart.mp4")

    def test_missing_title_requires_review(self):
        with self.assertRaisesRegex(ValueError, "title"):
            preview("/data/scenes", "$studio_name$", "$title$", {"studio_name": "Studio"}, ".mp4")

    def test_reject_traversal_invalid_template_and_bad_extension(self):
        for directory, filename, extension in (("../outside", "$title$", ".mp4"),
                                                ("$studio_name$", "$unknown$", ".mp4"),
                                                ("$studio_name$", "$title$", "/evil"),
                                                ("$studio_name$", "$title$", ".")):
            with self.subTest(directory=directory, filename=filename, extension=extension):
                with self.assertRaises(ValueError):
                    preview("/data/scenes", directory, filename, {"studio_name": "S", "title": "T"}, extension)

    def test_extension_is_always_retained(self):
        self.assertTrue(preview("/data/movies", "$studio_name$", "$title$",
                                {"studio_name": "S", "title": "T"}, ".mkv").endswith("/T.mkv"))


if __name__ == "__main__":
    unittest.main()
