const NUM_OF_TABS = 3
const openTab = (event, num) => {
    for (j = 1; j <= NUM_OF_TABS; j++) {
        num == j ? $(`#tab${j}`).show() : $(`#tab${j}`).hide()
    }
}

window.onload = () => {
    let selectedFileId = ''
    let selectedDirectoryId = '#'
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const $filesystemTree = $('#filesystem_tree');
    const $focusSection = $('#program-elements');

    const $addFileButton = $('#add-file-btn');
    const $addDirButton = $('#add-dir-btn');
    const $deleteButton = $('#delete-btn');

    const $logoutButton = $('#logout-btn')
    const $runButton = $('#run-btn')

    const $fileForm = $('#add-file-form');
    const $directoryForm = $('#add-dir-form');
    const $deleteForm = $('#delete-form');
    const $proversForm = $('#prover-form')
    const $vcsForm = $('#vcs-form')

    const $fileModal = $('#add-file-modal');
    const $directoryModal = $('#add-dir-modal');
    const $deleteModal = $('#delete-modal');

    const $resultTabContent = $('#result')

    const updateFramaOutput = (sections, logs) => {
        $focusSection.empty()

        for (const section of sections) {
            const key = Number(section.key)
            $focusSection.append('<br>').append($('<button>').addClass('section-button').attr('id', `focus-button-${key}`).html(section.name).click((event) => {
                $(`#focus${key}`).toggleClass('hide');
            }));
            $focusSection.append($('<pre>').addClass('section-inner-content').css("background-color", section.color).html(section.data).attr('id', `focus${key}`));
        }
        $resultTabContent.text(logs)

    }

    const fetchFile = (fileId) => {
        $.ajax({
            type: 'get',
            url: url_get_file,
            data: `file=${fileId}`,
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: (response) => {
                $('#file-text-content').text(response.source_code)
                
                updateFramaOutput(response.sections, response.logs)
            }
        })
    }



    $addFileButton.on('click', () => {
        $fileModal.show()
    })

    $addDirButton.on('click', () => {
        $directoryModal.show()
    })

    $deleteButton.on('click', () => {
        $deleteModal.show()
    })

    $logoutButton.on('click', () => {
        console.log('logout')

        $.ajax({
            type: 'POST',
            url: url_logout,
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: (reponse) => {
                location.reload()
            }
        })
    })

    $runButton.on('click', () => {
        $.ajax({
            type: 'GET',
            url: url_run,
            data: `file=${selectedFileId || ''}`,
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: (response) => {
                updateFramaOutput(response.sections, response.logs)
            }
        })
    })


    $(document).mouseup((e) => {
        if (!$fileModal.is(e.target) && $fileModal.has(e.target).length === 0) {
            $fileModal.hide()
        }

        if (!$directoryModal.is(e.target) && $directoryModal.has(e.target).length === 0) {
            $directoryModal.hide()
        }

        if (!$deleteModal.is(e.target) && $deleteModal.has(e.target).length === 0) {
            $deleteModal.hide()
        }
    })
        


    const resetView = () => {
        $('#file-text-content').val('Please select a file to open hehe')
        $focusSection.empty()
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
                    'headers': {
                        'X-CSRFToken': csrftoken
                    },

                    success: (data) => {
                        console.log(data)
                        $(data).each(() => ({ 'id': this.id, 'parent': this.parent, 'text': this.text }))
                    }
                },
                'plugins': ['state']
            }
        });

    $fileForm.submit((e) => {
        e.preventDefault();
        formData = new FormData($fileForm[0])
        // console.log(JSON.stringify(formData));
        $.ajax({
            type: 'POST',
            url: url_add_file,
            data: formData,
            headers: {
                'X-CSRFToken': csrftoken
            },
            contentType: false,
            processData: false, 
            success: (reponse) => {
                $filesystemTree.jstree(true).refresh();
                $fileModal.hide();
                $fileForm.trigger('reset');
            },
            error: (response) => {
                // alert the error if any error occured
                alert(response["responseJSON"]["error"]);
                console.log(response["responseJSON"]["error"]);
            }
        })
    })

    $directoryForm.submit((e) => {
        e.preventDefault();

        $.ajax({
            type: 'POST',
            url: url_add_dir,
            data: $directoryForm.serialize(),
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: (reponse) => {
                $filesystemTree.jstree(true).refresh();
                $directoryModal.css('display', 'none');
                $directoryForm.trigger('reset');
            },
            error: (response) => {
                // alert the error if any error occured
                alert(response["responseJSON"]["error"]);
            }
        })
    })

    $deleteForm.submit((e) => {
        e.preventDefault();

        $.ajax({
            type: 'POST',
            url: url_delete,
            data: $deleteForm.serialize(),
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: (reponse) => {
                $filesystemTree.jstree(true).refresh();
                $deleteModal.css('display', 'none');
                selectedDirectoryId = null
                selectedFileId = null
                $filesystemTree.jstree('select_node', '#')
            },
            error: (response) => {
                // alert the error if any error occured
                alert(response["responseJSON"]["error"]);
            }
        })
    })

    $proversForm.submit((e) => {
        e.preventDefault();

        $.ajax({
            type: 'POST',
            url: url_provers,
            data: $proversForm.serialize(),
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: (response) => {
                alert('Prover changed successfully')
            }
        })
    })

    $vcsForm.submit((e) => {
        e.preventDefault();

        $.ajax({
            type: 'POST',
            url: url_vcs,
            data: $vcsForm.serialize(),
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: (response) => {
                alert('Verification conditions changed successfully')
            }
        })
    })

}