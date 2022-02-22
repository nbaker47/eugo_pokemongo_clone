from django import forms

class lecMakerForm(forms.Form):
    duration= forms.IntegerField(label='duration /mins:')
    name= forms.CharField(label='lecture name')
    hp= forms.IntegerField(label='Health Points')
    attack= forms.IntegerField(label='attack')
    type = forms.CharField(label='Typing')
    sprite = forms.CharField(label='sprite' )
    coords= forms.CharField(label='coords')
    gameOp = forms.CharField(label='battle/spawn?')
