window.onload = () => {
    let selectedFileId = ''
    let selectedDirectoryId = '#'
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const $filesystemTree = $('#filesystem_tree');

    const fetchFile = (fileId) => {
        $.ajax({
            type: 'get',
            url: url_get_file,
            data: `file=${fileId}`,
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: (response) => {
                $('#source-code-text-area').val(response.source_code)

                $focusSection.empty()

                for (const section of response.sections) {
                    const key = Number(section.key)
                    $focusSection.append($('<button>').addClass('section-button').attr('id', `focus-button-${key}`).html(section.name).click((event) => {
                        $(`#focus${section.key}`).toggleClass('hide');
                    }));
                    $focusSection.append($('<div>').addClass('section-inner-content').html(section.description).attr('id', `focus${key}`));
                }
            }
        })
    }

    $filesystemTree
        .on('changed.jstree', (event, data) => {
            const node = data.node

            if (node) {
                if (node.id === '#') {
                    selectedFileId = null
                    selectedDirectoryId = null
                    resetView()
                } else if (node.id.substr(0, 3) === 'dir') {
                    selectedDirectoryId = node.id.substr(3, node.id.length - 3)
                    selectedFileId = null
                    resetView()
                } else {
                    selectedFileId = node.id.substr(3, node.id.length - 3)
                    selectedDirectoryId = node.parent === '#' ? null : node.parent.substr(3, node.parent.length - 3)
                    fetchFile(selectedFileId)
                }
            }
        })
        .jstree({
            'core': {
                'data': {
                    'type': 'GET',
                    'url': url_get_filesystem_tree,
                    'contentType': 'application/json; charset=utf-8',

                    success: (data) => {
                        $(data).each(() => ({'id': this.id, 'parent': this.parent, 'text': this.text}))
                    }
                },
                'plugins': ['state']
            }
        });
}