from django import forms
from .models import Atelier, Inscription, InscriptionConference


class InscriptionForm(forms.ModelForm):
    atelier = forms.CharField(
        max_length=100,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_atelier'}),
        label='Atelier thématique',
    )

    class Meta:
        model = Inscription
        fields = [
            'nom', 'prenom', 'email', 'whatsapp', 'institution',
            'fonction', 'profil', 'profil_autre', 'atelier', 'engagement',
            'source_connaissance', 'source_connaissance_courrier_numero',
            'motivation', 'validation_engagement',
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
                'id': 'id_atelier',
            }),
            'engagement': forms.Select(attrs={
                'class': 'form-select',
            }),
            'source_connaissance': forms.RadioSelect(attrs={
                'class': 'form-check-input',
            }),
            'source_connaissance_courrier_numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'N° du courrier, si possible',
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
        self.fields['source_connaissance'].required = False

        ateliers = list(Atelier.objects.filter(active=True).order_by('ordre', 'label').values_list('code', 'label'))
        choices = [('', '--- Sélectionner un atelier ---')] + ateliers
        self.fields['atelier'].widget.choices = choices

        # Remove empty choice from radio buttons
        self.fields['source_connaissance'].choices = Inscription.SOURCE_CONNAISSANCE_CHOICES

    def clean_atelier(self):
        value = self.cleaned_data.get('atelier', '').strip()
        if not value:
            raise forms.ValidationError('Veuillez sélectionner un atelier thématique.')
        return value

    def _post_clean(self):
        atelier_ok = self.cleaned_data.get('atelier')
        super()._post_clean()
        if atelier_ok and 'atelier' in self._errors:
            del self._errors['atelier']
            self.cleaned_data['atelier'] = atelier_ok

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


class InscriptionConferenceForm(forms.ModelForm):
    """Formulaire d'inscription du public à la conférence DounIA."""

    class Meta:
        model = InscriptionConference
        fields = ['nom', 'prenom', 'email', 'telephone', 'organisation', 'categorie']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre nom de famille',
            }),
            'prenom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Vos prénoms',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'exemple@email.com',
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+224 XXX XX XX XX',
            }),
            'organisation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre organisation (optionnel)',
            }),
            'categorie': forms.Select(attrs={
                'class': 'form-select',
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if InscriptionConference.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Cette adresse email est déjà inscrite à la conférence.'
            )
        return email

