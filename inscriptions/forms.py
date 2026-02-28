from django import forms
from .models import Atelier, Inscription


class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = [
            'nom', 'prenom', 'email', 'whatsapp', 'institution',
            'fonction', 'profil', 'profil_autre', 'atelier', 'engagement',
            'format_preference', 'disponibilite', 'motivation',
            'validation_engagement',
        ]
        labels = {
            'prenom': 'Prénoms',
        }
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre nom de famille',
            }),
            'prenom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre prénom',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'exemple@email.com',
            }),
            'whatsapp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+224 XXX XX XX XX',
            }),
            'institution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de votre institution ou organisation',
            }),
            'fonction': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre fonction ou poste actuel',
            }),
            'profil': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_profil',
            }),
            'profil_autre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Précisez votre profil...',
            }),
            'atelier': forms.Select(attrs={
                'class': 'form-select',
            }),
            'engagement': forms.Select(attrs={
                'class': 'form-select',
            }),
            'format_preference': forms.Select(attrs={
                'class': 'form-select',
            }),
            'disponibilite': forms.Select(attrs={
                'class': 'form-select',
            }),
            'motivation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'maxlength': 200,
                'placeholder': 'Expliquez brièvement votre motivation pour participer à cet atelier (optionnel, 500 caractères max)...',
            }),
            'validation_engagement': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['motivation'].required = False
        self.fields['profil_autre'].required = False

        ateliers = list(Atelier.objects.filter(active=True).order_by('ordre', 'label').values_list('code', 'label'))
        if ateliers:
            self.fields['atelier'].choices = ateliers

    def clean(self):
        cleaned_data = super().clean()
        profil = cleaned_data.get('profil')
        profil_autre = cleaned_data.get('profil_autre', '').strip()
        if profil == 'autre' and not profil_autre:
            self.add_error('profil_autre', 'Veuillez préciser votre profil.')
        return cleaned_data

    def clean_validation_engagement(self):
        value = self.cleaned_data.get('validation_engagement')
        if not value:
            raise forms.ValidationError(
                'Vous devez vous engager à participer activement pour valider votre inscription.'
            )
        return value

