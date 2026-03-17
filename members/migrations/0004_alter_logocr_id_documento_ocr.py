from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0003_documentosocr_cic_ocrid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logocr',
            name='id_documento_ocr',
            field=models.ForeignKey(db_column='idDocumentoOCR', on_delete=django.db.models.deletion.CASCADE, to='members.documentosocr'),
        ),
    ]
