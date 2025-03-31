from stash_heresphere.hello import say_hello

def test_say_hello(capsys):
    say_hello()
    captured = capsys.readouterr()
    assert captured.out == "Hello, world\n"