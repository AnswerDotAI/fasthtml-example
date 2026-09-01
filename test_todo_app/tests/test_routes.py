def test_landing_page(test_client_and_database):
    client, todos = test_client_and_database
    res = client.get("/")
    assert res.status_code == 200
    assert "Todo list" in res.text
    assert todos.count == 0

def test_adding_new_todo(test_client_and_database):
    client, todos = test_client_and_database
    res = client.post("/", data={"title": "Test Todo"})
    assert res.status_code == 200
    assert todos.count == 1
    assert todos.get(1).title == "Test Todo"

def test_updating_existing_todo(test_client_and_database):
    client, todos = test_client_and_database
    todos.insert({"title": "Test Todo"})

    res = client.put("/", data={"id": 1, "title": "Updated Todo", "done": 1})
    assert res.status_code == 200

    assert todos.count == 1
    assert todos.get(1).title == "Updated Todo"
    assert todos.get(1).done == True

def test_deleting_existing_todo(test_client_and_database):
    client, todos = test_client_and_database
    todos.insert({"title": "Test Todo"})

    res = client.delete("/todos/1")
    assert res.status_code == 200
    assert todos.count == 0
