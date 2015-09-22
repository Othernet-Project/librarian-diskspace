import mock

from librarian_diskspace import zipballs as mod


@mock.patch.object(mod.os.path, 'abspath')
@mock.patch.object(mod, 'filewalk')
@mock.patch.object(mod.os, 'stat')
def test_get_content_size(os_stat, to_path, filewalk, abspath):
    filewalk.return_value = ['/path/to/content/s/o/m/e/m/d/5']
    mocked_stat = mock.Mock(st_size=1024)
    os_stat.return_value = mocked_stat
    size = mod.get_content_size('some_md5', '/path/to/content')
    assert size == 1024
    os_stat.assert_called_once_with('/path/to/content/s/o/m/e/m/d/5')
    to_path.assert_called_once_with('some_md5', prefix='/path/to/content')


@mock.patch.object(mod, 'get_content_size')
@mock.patch.object(mod, 'clone_zipball')
@mock.patch.object(mod, 'needed_space')
@mock.patch.object(mod, 'get_old_content')
@mock.patch.object(mod, 'request')
def test_cleanup_list(request, get_old_content, needed_space, clone_zipball,
                      get_content_size):
    free_space = 123456
    request.app.config = {'library.contentdir': '/path/to/content'}
    needed_space.return_value = 1000
    clone_zipball.side_effect = lambda x: x
    get_content_size.return_value = 400
    fake_zipballs = [
        {'md5': 'first', 'size': 300},
        {'md5': 'second', 'size': 350},
        {'md5': 'third'}
    ]
    get_old_content.return_value = fake_zipballs

    for i, zipball in enumerate(mod.cleanup_list(free_space)):
        assert zipball['md5'] == fake_zipballs[i]['md5']
        assert 'size' in zipball

    needed_space.assert_called_once_with(free_space, config=request.app.config)
    get_content_size.assert_called_once_with('third', '/path/to/content')
