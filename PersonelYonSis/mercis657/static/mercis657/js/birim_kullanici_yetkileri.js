// Yetkili Kullanıcılar Modalı
function openYetkiliKullanicilarModal(birimId) {
    // Yetkili kullanıcılar modalını aç
    var modal = new bootstrap.Modal(document.getElementById('yetkiliKullanicilarModal'));
    modal.show();
    fetch(`/mercis657/birim/${birimId}/yetkililer/`)
        .then(resp => resp.json())
        .then(data => {
            const ul = document.getElementById('yetkiliKullanicilarListesi');
            ul.innerHTML = '';
            if (data.status === 'success' && Array.isArray(data.data)) {
                data.data.forEach(user => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item d-flex justify-content-between align-items-center';
                    li.innerHTML = `
                        <span>${user.username} - ${user.full_name}</span>
                        <button class="btn btn-danger btn-sm" onclick="kullaniciYetkiSil(${birimId},'${user.username}', this)">
                            <i class="bi bi-trash"></i>
                        </button>
                    `;
                    ul.appendChild(li);
                });
            } else {
                ul.innerHTML = '<li class="list-group-item text-muted">Yetkili kullanıcı yok.</li>';
            }
        });
    document.getElementById('kullaniciAraInput').value = '';
    document.getElementById('kullaniciAraSonuc').innerHTML = '';
    const form = document.getElementById('yetkiliKullaniciEkleForm');
    form.onsubmit = function(e) {
        e.preventDefault();
        const username = document.getElementById('kullaniciAraInput').value.trim();
        if (!username) return;
        fetch(`/mercis657/kullanici/ara/?username=${encodeURIComponent(username)}`)
            .then(resp => resp.json())
            .then(data => {
                const sonucDiv = document.getElementById('kullaniciAraSonuc');
                if (data.status === 'success' && data.data) {
                    const user = data.data;
                    sonucDiv.innerHTML = `
                        <div class="alert alert-success d-flex justify-content-between align-items-center mb-2">
                            <span>${user.username} - ${user.full_name}</span>
                            <button class="btn btn-primary btn-sm" id="btnYetkiVer">
                                <i class="bi bi-person-plus"></i> Yetki Ver
                            </button>
                        </div>
                    `;
                    document.getElementById('btnYetkiVer').onclick = function() {
                        fetch(`/mercis657/birim/${birimId}/yetki-ekle/`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': '{{ csrf_token }}'
                            },
                            body: JSON.stringify({ username: user.username })
                        })
                        .then(resp => resp.json())
                        .then(res => {
                            if (res.status === 'success') {
                                sonucDiv.innerHTML = '<div class="alert alert-success">Yetki verildi.</div>';
                                openYetkiliKullanicilarModal(birimId);
                            } else {
                                sonucDiv.innerHTML = `<div class="alert alert-danger">${res.message || 'Yetki verilemedi.'}</div>`;
                            }
                        });
                    };
                } else {
                    sonucDiv.innerHTML = `<div class="alert alert-danger">Kullanıcı bulunamadı.</div>`;
                }
            });
    };
}

function kullaniciYetkiSil(birimId, username, btn) {
    if (!confirm('Bu kullanıcının yetkisini kaldırmak istiyor musunuz?')) return;
    fetch(`/mercis657/birim/${birimId}/yetki-sil/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify({ username: username })
    })
    .then(resp => resp.json())
    .then(res => {
        if (res.status === 'success') {
            btn.closest('li').remove();
        } else {
            alert(res.message || 'Yetki silinemedi.');
        }
    });
}