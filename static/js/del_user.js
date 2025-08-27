function del(currentUserId){
    let conf = confirm("Вы действительно хотите удалить этого пользователя?")
    if (conf){
    let id_ = this.getAttribute("value");
    if (currentUserId != id_){
    fetch('/api/v2/users/' + id_, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
            })
    let parentRow = this.parentElement.parentElement.parentElement;
    parentRow.remove();
}
else {
    let errors = document.getElementById("errors");
    errors.textContent = "Нельзя удалить самого себя";
}}}