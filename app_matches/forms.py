from django import forms

from .models import Match, Bet


class MatchFilterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MatchFilterForm, self).__init__(*args, **kwargs)
        self.fields['home_team'].required = False
        self.fields['away_team'].required = False

    class Meta:
        model = Match
        fields = ('home_team', 'away_team',)
        widgets = {'home_team': forms.Select(attrs={'onchange': 'form.submit();'}),
                   'away_team': forms.Select(attrs={'onchange': 'form.submit();'}),
                   }
        labels = {'home_team': 'Home Team',
                  'away_team': 'Away Team', }


class BetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BetForm, self).__init__(*args, **kwargs)
        self.fields['bet_amt'].required = False

    class Meta:
        model = Bet
        fields = ('bet_amt', )
        labels = {'bet_amt': "Amount", }
        widgets = {'bet_amt': forms.HiddenInput()}


class MatchWinnerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MatchWinnerForm, self).__init__(*args, **kwargs)
        self.fields['winner'].required = False
        self.fields['home_team_score'].required = False
        self.fields['away_team_score'].required = False
        self.fields['result'].required = False

    class Meta:
        model = Match
        fields = ('winner', 'home_team_score',
                  'away_team_score', 'result')


class MatchDefaultBetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MatchDefaultBetForm, self).__init__(*args, **kwargs)
        self.fields['match'].required = False

    class Meta:
        model = Bet
        fields = ('match',)
