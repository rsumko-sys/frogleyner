import pytest
from db import Database
import asyncio
import os
import tempfile

@pytest.mark.asyncio
async def test_db_crud():
    db_path = tempfile.mktemp(suffix=".db")
    db = Database(db_path)
    await db.connect()
    await db.upsert_user(123, first_name="Test")
    user = await db.get_user(123)
    assert user["user_id"] == 123
    assert user["first_name"] == "Test"
    await db.close()
    os.remove(db_path)
