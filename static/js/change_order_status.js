function setOrderAsReady(id_){
    fetch('/api/v2/orders/' + id_, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            json={
                "yet_to_cook": false
            }
            })
    this.remove()
}