from dataclasses import dataclass
import unicodedata


# SPEC: https://qr-platba.cz/pro-vyvojare/specifikace-formatu/

@dataclass
class Payment:
    ACC: str
    AM: float
    MSG: str = None
    CC: str = "CZK"
    DT: str = None
    X_VS: int = None
    X_SS: int = None
    X_KS: int = None

    @property
    def acc(self):
        acc = self.ACC
        acc = acc.replace(" ", "")
        return f"*ACC:{acc}"

    @property
    def am(self):
        am = float(self.AM)
        return f"*AM:{am:.2f}"

    @property
    def cc(self):
        return f"*CC:{self.CC}"

    @property
    def dt(self):
        dt = self.DT
        return f"*DT:{dt}" if self.DT else ""

    @property
    def msg(self):
        msg = self.MSG[:60] if self.MSG else ""
        nfkd_form = unicodedata.normalize('NFKD', msg)
        msg_normalied = (u"".join([c for c in nfkd_form if not unicodedata.combining(c)]))
        msg_normalied = msg_normalied.upper()
        msg_normalied = msg_normalied.encode("ISO-8859-1", "ignore").decode()
        msg_normalied = msg_normalied.replace("*", "_")

        return f"*MSG:{msg_normalied}" if self.MSG else ""

    @property
    def vs(self):
        vs = str(self.X_VS)[-10:]
        return f"*X-VS:{vs}" if self.X_VS else ""

    @property
    def ss(self):
        ss = str(self.X_SS)[-10:]
        return f"*X-SS:{ss}" if self.X_SS else ""

    @property
    def ks(self):
        ks = str(self.X_KS)[-10:]
        return f"*X_KS:{ks}" if self.X_KS else ""


class StrGenerator:
    def __init__(self, iban: str, ammount: int, message: str = None, vs: int = None, ss: int = None, ks: int = None):
        self.payment = Payment(ACC=iban, AM=ammount, MSG=message)
        self.payment.X_VS = vs
        self.payment.X_SS = ss
        self.payment.X_KS = ks

    def generate_string(self) -> str:
        payment = self.payment
        result = f"SPD*1.0{payment.acc}{payment.am}{payment.cc}{payment.dt}{payment.msg}{payment.vs}{payment.ks}{payment.ss}"
        return result
