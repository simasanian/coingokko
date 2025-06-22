from django import forms
from core.models import User

#送金元（Sender）を固定する前の記述
#class TransactionForm(forms.Form):
#    sender = forms.ModelChoiceField(queryset=User.objects.all(), label="送信者")
#    receiver = forms.ModelChoiceField(queryset=User.objects.all(), label="受信者")
#    amount = forms.IntegerField(min_value=1, label="送金額")

class TransactionForm(forms.Form):
    sender = forms.ModelChoiceField(queryset=User.objects.none(), label="送信者", required=True)
    receiver = forms.ModelChoiceField(queryset=User.objects.all(), label="受信者")
    amount = forms.IntegerField(min_value=1, label="送金額")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # 呼び出し元からuserを受け取る
        super(TransactionForm, self).__init__(*args, **kwargs)
#        super().__init__(*args, **kwargs)
        if user:
            self.fields['sender'].queryset = User.objects.filter(id=user.id)
            self.fields['sender'].initial = user  # 初期値セット（選択欄1択にする）


class AddUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='パスワード')
    balance = forms.IntegerField(min_value=0, initial=0, label='初期残高')

    class Meta:
        model = User
        fields = ['username', 'password', 'balance']
