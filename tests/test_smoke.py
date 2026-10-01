"""اختبارات أساسية لـHALA"""
from click.testing import CliRunner
from hala.cli import main
from hala.commands.nlp import analyze


def test_version():
    r = CliRunner().invoke(main, ["--version"])
    assert r.exit_code == 0
    assert "0.1.0" in r.output


def test_help():
    r = CliRunner().invoke(main, ["--help"])
    assert r.exit_code == 0
    assert "kashif" in r.output
    assert "sitr" in r.output
    assert "athar" in r.output
    assert "sayyad" in r.output
    assert "nlp" in r.output


def test_nlp_scam():
    """رسالة فيها OTP + جائزة → SCAM"""
    r = analyze("مبروك فزت بجائزة، أرسل OTP")
    assert r["verdict"] in ("SCAM", "SUSPICIOUS")
    assert r["score"] >= 30
    assert len(r["hits"]) > 0


def test_nlp_clean():
    """رسالة عادية → CLEAN"""
    r = analyze("مرحبا كيف حالك؟")
    assert r["verdict"] == "CLEAN"
    assert r["score"] < 30


def test_nlp_otp_only():
    """طلب OTP لحاله → SUSPICIOUS على الأقل"""
    r = analyze("أرسل لي رمز التحقق من فضلك")
    assert r["verdict"] in ("SCAM", "SUSPICIOUS")


def test_kashif_invalid():
    """رقم غلط → exit code 2"""
    r = CliRunner().invoke(main, ["kashif", "abc"])
    assert r.exit_code == 2
