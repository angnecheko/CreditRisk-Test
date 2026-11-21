from app.validation import DemandeCredit


def test_conserve_les_montants_en_fcfa(demande):
    entree = DemandeCredit.model_validate(demande)
    assert entree.revenu_mensuel == 250000
    assert entree.montant_credit == 1000000
