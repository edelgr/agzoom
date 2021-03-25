from django.forms import ModelForm, DateInput
from .models import Image, Shape


class NewImageModelForm(ModelForm):
    class Meta:
        model = Image
        fields = '__all__'
        widgets = {
            'date_captured': DateInput(attrs={'type': 'date'}),
        }


class NewShapeFileModelForm(ModelForm):
    class Meta:
        model = Shape
        fields = '__all__'
        widgets = {
            'date_captured': DateInput(attrs={'type': 'date'}),
        }

