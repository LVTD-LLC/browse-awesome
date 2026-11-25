from django.db import migrations


def correct_title(apps, schema_editor):
    awesome_list = apps.get_model("repos", "AwesomeList")
    awesome_list.objects.using(schema_editor.connection.alias).filter(
        slug="awesome-chatgpt",
        source_url="https://github.com/uhub/awesome-chatgpt",
        repo_full_name="uhub/awesome-llm",
        name="Awesome Chatgpt",
    ).update(name="Awesome LLM (formerly Awesome ChatGPT)")


class Migration(migrations.Migration):
    dependencies = [("repos", "0023_repository_repo_created_desc_idx")]
    operations = [migrations.RunPython(correct_title, migrations.RunPython.noop)]
