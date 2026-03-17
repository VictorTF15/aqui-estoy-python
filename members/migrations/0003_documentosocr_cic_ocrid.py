from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0002_alter_tipousuario_options_alter_usuarios_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentosocr',
            name='cic_extraido',
            field=models.CharField(blank=True, max_length=9, null=True),
        ),
        migrations.AddField(
            model_name='documentosocr',
            name='ocr_id_cr_extraido',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
    ]
