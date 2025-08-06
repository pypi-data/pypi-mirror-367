# pidalu-core

Reusable Django core utilities and base components for Django and Django REST Framework projects.

> Includes model mixins, serializer tools, queryset managers, admin helpers, and middleware.  
> Designed to work out of the box with `settings.py` overrides.

---

## 🚀 Features

### ✅ Models & Mixins

-   `TimeStampedModel` – auto `created_at`, `updated_at`
-   `UserTrackerModel` – auto `created_by`, `updated_by`
-   `TrackedModel` – combo of the above
-   `SlugFieldModel` – auto slug from any source field
-   `UUIDPrimaryKeyModel` – use UUIDs as primary keys
-   `SoftDeleteModel` – soft deletion with manager/queryset support
-   `AuditModel` – tracks and logs field-level changes
-   `GenericRelationModel` – abstract base model for `GenericForeignKey` support

### 🔁 QuerySet & Manager Extensions

-   `SoftDeleteManager` – `.only_deleted()`, `.with_deleted()`, `.active()`
-   `SoftDeleteQuerySet` – compatible with manager above

### 📦 Serializers

-   `DynamicFieldsModelSerializer` – limit output via `fields=[...]`
-   `DynamicFieldsSerializer` – same for plain serializers
-   `DummySerializer` – no-op placeholder
-   _(All located in `pidalu_core.serializers`)_

### 🛠 Admin Helpers

-   `ReadOnlyAdminFieldsMixin` – make selected fields readonly
-   `AutoSlugAdminMixin` – auto-prepopulate `slug` in admin from any field

### 🧠 Middleware

-   `RequestMiddleware` – stores current request in thread-local
    > Used to track `created_by`/`updated_by` automatically in models

---

## ⚙️ Installation

```bash
pip install pidalu-core
```

Or using Poetry:

```bash
poetry add pidalu-core
```

---

## 🧩 Setup

### 1. Add Middleware

```python
# settings.py
MIDDLEWARE = [
    "pidalu_core.middleware.RequestMiddleware",  # ✅ Add near top
    ...
]
```

### 2. Optional Settings

```python
# settings.py

PIDALU_CORE_AUTO_SLUG_FIELD = "name"  # default source field for slug generation
```

---

## 🧱 Usage Examples

### `TrackedModel` (timestamps + user)

```python
from pidalu_core.models import TrackedModel

class Post(TrackedModel):
    title = models.CharField(max_length=100)
```

### `SlugFieldModel` with custom source

```python
class Article(SlugFieldModel):
    title = models.CharField(max_length=255)
    slug_source_field = "title"
```

### `SoftDeleteModel` with manager

```python
class Project(SoftDeleteModel):
    name = models.CharField(max_length=255)

# Usage:
Project.objects.all()  # active only
Project.objects.only_deleted()
Project.objects.with_deleted()
```

### `GenericRelationModel` (generic foreign key)

```python
from pidalu_core.models import GenericRelationModel

class Tag(GenericRelationModel):
    label = models.CharField(max_length=50)

# Usage:
# Tag can be attached to any model instance via `content_type` and `object_id`
```

### `DynamicFieldsModelSerializer`

```python
class UserSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]

# usage: UserSerializer(user, fields=["id", "email"])
```

`request` object is a cached property in Dynamic serializers, you can access request object directly without going through context.

```python
class UserSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]

    def get_fields(self):
        fields = super().get_fields()
        if self.request.method.lower() == 'get':  # directly access request object
            fields["details"] = UserDetailSerializer(fields=["address", "bio"])
        return fields
```

---

## 🧪 Testing

Use `Makefile` > `test`.

### Setup

```bash
make test
```

Or directly with Poetry, uses pytest and pytest-django under the hood:

```bash
PYTHONPATH=. poetry run pytest -vv
```

We use in-memory SQLite + dynamic schema creation.

---

## 👤 Author

Built and maintained by **Pidalu Tech Team**.

---

## 🪪 License

MIT License — free to use, modify, and distribute.
