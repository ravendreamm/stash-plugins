import unittest

from plugin import CONFIG_QUERY, run


class FakeStash:
    def __init__(self, enabled=True, scene=None):
        self.enabled = enabled
        self.scene = scene
        self.calls = []

    def call_GQL(self, query, variables=None):
        self.calls.append((query, variables))
        if query == CONFIG_QUERY:
            return {"configuration": {"plugins": {"stash-rename-preview": {"enabled": self.enabled}}}}
        return {"findScene": self.scene}


class FakeLog:
    def __init__(self):
        self.messages = []

    def info(self, message):
        self.messages.append(message)

    def warning(self, message):
        self.messages.append(message)


class PluginTest(unittest.TestCase):
    def test_update_previews_only_the_requested_scene(self):
        stash = FakeStash(scene={"title": "Example", "tags": [], "files": [{"id": "2", "path": "/data/unmatched/a.mp4"}]})
        log = FakeLog()
        run({"args": {"hookContext": {"type": "Scene.Update.Post", "id": "5"}}}, stash, log)
        self.assertEqual(stash.calls[1][1], {"id": "5"})
        self.assertIn("/data/scenes/Example/Example.mp4", log.messages[0])
        self.assertTrue(all(call[0].lstrip().startswith("query ") for call in stash.calls))

    def test_disabled_does_not_retrieve_scene(self):
        stash = FakeStash(enabled=False)
        run({"args": {"hookContext": {"type": "Scene.Update.Post", "id": "5"}}}, stash, FakeLog())
        self.assertEqual(len(stash.calls), 1)

    def test_movie_tag_and_missing_title(self):
        stash = FakeStash(scene={"tags": [{"name": "Movie"}], "files": [{"path": "/data/unmatched/a.mp4"}]})
        log = FakeLog()
        run({"args": {"hookContext": {"type": "Scene.Update.Post", "id": "5"}}}, stash, log)
        self.assertIn("Missing required metadata: title", log.messages[0])

    def test_unrelated_event_does_nothing(self):
        stash = FakeStash()
        run({"args": {"hookContext": {"type": "Scene.Create.Post", "id": "5"}}}, stash, FakeLog())
        self.assertEqual(stash.calls, [])


if __name__ == "__main__":
    unittest.main()
