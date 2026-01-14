document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const uploadPreview = document.getElementById('uploadPreview');
    const fileInput = document.getElementById('fileInput');
    const clearUploadBtn = document.getElementById('clearUpload');
    const generateBtn = document.getElementById('generateBtn');
    const btnText = generateBtn.querySelector('.btn-text');
    const btnLoading = generateBtn.querySelector('.btn-loading');
    const resultPlaceholder = document.getElementById('resultPlaceholder');
    const resultImage = document.getElementById('resultImage');
    const saveBtn = document.getElementById('saveBtn');

    let uploadedImageData = null;

    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });

    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    function handleFile(file) {
        const validTypes = ['image/png', 'image/jpeg', 'image/jpg'];
        if (!validTypes.includes(file.type)) {
            alert('PNG、JPG、JPEG形式の画像のみアップロードできます。');
            return;
        }

        const maxSize = 16 * 1024 * 1024;
        if (file.size > maxSize) {
            alert('ファイルサイズは16MB以下にしてください。');
            return;
        }

        const reader = new FileReader();
        reader.onload = function(e) {
            uploadedImageData = e.target.result;
            uploadPreview.src = uploadedImageData;
            uploadPreview.classList.remove('hidden');
            uploadPlaceholder.classList.add('hidden');
            clearUploadBtn.classList.remove('hidden');
            generateBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    }

    clearUploadBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        clearUpload();
    });

    function clearUpload() {
        uploadedImageData = null;
        uploadPreview.src = '';
        uploadPreview.classList.add('hidden');
        uploadPlaceholder.classList.remove('hidden');
        clearUploadBtn.classList.add('hidden');
        generateBtn.disabled = true;
        fileInput.value = '';
    }

    generateBtn.addEventListener('click', async function() {
        if (!uploadedImageData) {
            alert('画像をアップロードしてください。');
            return;
        }

        const carModel = document.querySelector('input[name="car_model"]:checked').value;
        const drivingMode = document.querySelector('input[name="driving_mode"]:checked').value;

        setLoading(true);

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: uploadedImageData,
                    car_model: carModel,
                    driving_mode: drivingMode
                })
            });

            const data = await response.json();

            if (data.success) {
                resultImage.src = data.image;
                resultImage.classList.remove('hidden');
                resultPlaceholder.classList.add('hidden');
                saveBtn.classList.remove('hidden');
                
                if (data.dry_run) {
                    console.log('DRY RUN mode: Using placeholder image');
                }
            } else {
                alert('エラーが発生しました: ' + (data.error || '不明なエラー'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('通信エラーが発生しました。もう一度お試しください。');
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        if (isLoading) {
            generateBtn.disabled = true;
            btnText.classList.add('hidden');
            btnLoading.classList.remove('hidden');
        } else {
            generateBtn.disabled = !uploadedImageData;
            btnText.classList.remove('hidden');
            btnLoading.classList.add('hidden');
        }
    }

    saveBtn.addEventListener('click', async function() {
        const imageData = resultImage.src;
        
        if (!imageData) {
            alert('保存する画像がありません。');
            return;
        }

        try {
            const response = await fetch('/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: imageData
                })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'ai_car_designer_result.png';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else {
                alert('ダウンロードに失敗しました。');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('ダウンロードエラーが発生しました。');
        }
    });
});
