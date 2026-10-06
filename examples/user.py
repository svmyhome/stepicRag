from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: int
    name: str = 'Joe'

user1 = User(id=1)
# print(user1.name)
# print(user1.__dict__)
# print(user1, id(user1))
# print(user1.model_dump())
# print(user1.model_dump_json())
# user2 = user1.model_copy()
# print(user2, id(user2))
raw_user = {"id": 12345, "name": "Анна"}
user3 = User.model_validate(raw_user)
print(user3, id(user3))
print(User.model_json_schema())
print(User.model_fields["id"].annotation)
raw_user2 = {"id": 12345}
user4 = User.model_validate(raw_user2)
print(user4, id(user4))
print(user4.model_fields_set)

