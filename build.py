"""Generate every error page from template.html.

The pages are served verbatim by Traefik from GitHub Pages, so each one must stay a
single self-contained HTML file: the template is expanded here, never at request time.
Run `make` (or `python3 build.py`) after editing the template or the copy below.
"""

from pathlib import Path
from string import Template

ROOT = Path(__file__).parent


def actions(*buttons):
    """Render the action row; the first button is the primary one."""
    links = []
    for index, (href, fr, en) in enumerate(buttons):
        css = "button button--primary" if index == 0 else "button"
        links.append(
            f'          <a class="{css}" href="{href}">\n'
            f'            <span data-lang="en">{en}</span>\n'
            f'            <span data-lang="fr">{fr}</span>\n'
            f"          </a>"
        )
    return '\n        <div class="actions">\n' + "\n".join(links) + "\n        </div>"


HOME = ("/", "Retour à l’accueil", "Back to the home page")
APP = ("https://invest.anantys.com", "Ouvrir l’application", "Open the app")
RETRY = ("", "Réessayer", "Try again")

COUNTDOWN_BLOCK = """
        <div class="status">
          <span data-lang="en">This page reloads automatically in</span>
          <span data-lang="fr">Cette page se recharge automatiquement dans</span>
          <time id="countdown">60 s</time>
        </div>"""

COUNTDOWN_SCRIPT = """
      var remaining = 60;
      var countdown = document.getElementById("countdown");
      setInterval(function () {
        remaining -= 1;
        if (remaining <= 0) {
          location.reload();
          return;
        }
        countdown.textContent = remaining + " s";
      }, 1000);"""

MAINTENANCE = dict(
    title_fr="Maintenance en cours",
    title_en="Maintenance in progress",
    label_class=" label--live",
    label_fr="Maintenance en cours",
    label_en="Maintenance in progress",
    h1_fr="Anantys revient dans quelques instants",
    h1_en="Anantys will be back shortly",
    p_fr="Le service est momentanément indisponible pendant une opération de maintenance.\n"
    "            Vos données et vos portefeuilles restent en sécurité.",
    p_en="The service is temporarily unavailable while we carry out maintenance.\n"
    "            Your data and your portfolios remain safe.",
    block=COUNTDOWN_BLOCK,
    script=COUNTDOWN_SCRIPT,
)

NOT_FOUND = dict(
    title_fr="Page introuvable",
    title_en="Page not found",
    label_fr="Erreur 404",
    label_en="Error 404",
    h1_fr="Cette page n’existe pas",
    h1_en="This page does not exist",
    p_fr="Le lien que vous avez suivi est peut-être ancien, ou l’adresse contient une erreur.",
    p_en="The link you followed may be out of date, or the address contains a typo.",
    block=actions(HOME, APP),
)

INTERNAL_ERROR = dict(
    title_fr="Erreur serveur",
    title_en="Server error",
    label_fr="Erreur serveur",
    label_en="Server error",
    h1_fr="Une erreur est survenue de notre côté",
    h1_en="Something went wrong on our side",
    p_fr="Cette page n’a pas pu s’afficher à cause d’un incident sur nos serveurs. L’équipe en est\n"
    "            informée. Vos données et vos portefeuilles restent en sécurité.",
    p_en="This page could not be displayed because of an incident on our servers. The team has\n"
    "            been notified. Your data and your portfolios remain safe.",
    block=actions(RETRY, HOME),
)

BAD_REQUEST = dict(
    title_fr="Requête invalide",
    title_en="Bad request",
    label_fr="Erreur 400",
    label_en="Error 400",
    h1_fr="Cette demande n’a pas pu être traitée",
    h1_en="This request could not be processed",
    p_fr="L’adresse ou les informations envoyées ne sont pas valides. Revenez à la page\n"
    "            précédente et réessayez.",
    p_en="The address or the information sent is not valid. Go back to the previous page\n"
    "            and try again.",
    block=actions(HOME, APP),
)

UNAUTHORIZED = dict(
    title_fr="Connexion requise",
    title_en="Sign-in required",
    label_fr="Connexion requise",
    label_en="Sign-in required",
    h1_fr="Connectez-vous pour accéder à cette page",
    h1_en="Sign in to access this page",
    p_fr="Votre session a peut-être expiré. Reconnectez-vous depuis l’application pour\n"
    "            continuer.",
    p_en="Your session may have expired. Sign in again from the app to continue.",
    block=actions(APP, HOME),
)

FORBIDDEN = dict(
    title_fr="Accès refusé",
    title_en="Access denied",
    label_fr="Accès refusé",
    label_en="Access denied",
    h1_fr="Vous n’avez pas accès à cette page",
    h1_en="You do not have access to this page",
    p_fr="Votre compte ne dispose pas des droits nécessaires pour afficher ce contenu. Si vous\n"
    "            pensez qu’il s’agit d’une erreur, écrivez-nous.",
    p_en="Your account does not have the rights needed to display this content. If you think\n"
    "            this is a mistake, write to us.",
    block=actions(HOME, APP),
)

# Ticker slope per tick: the quote recovers during a maintenance, drifts flat on a
# client error and rebounds after a server error.
RECOVERING, FLAT, REBOUNDING = 0.16, 0.0, 0.09

# Traefik serves maintenance, not_found and internal_error; the numbered pages
# answer direct links to the CDN and must look the same. The quote is the status.
PAGES = {
    "maintenance.html": (MAINTENANCE, 503, RECOVERING),
    "502.html": (MAINTENANCE, 502, RECOVERING),
    "503.html": (MAINTENANCE, 503, RECOVERING),
    "504.html": (MAINTENANCE, 504, RECOVERING),
    "not_found.html": (NOT_FOUND, 404, FLAT),
    "404.html": (NOT_FOUND, 404, FLAT),
    "internal_error.html": (INTERNAL_ERROR, 500, REBOUNDING),
    "500.html": (INTERNAL_ERROR, 500, REBOUNDING),
    "default.html": (INTERNAL_ERROR, 500, REBOUNDING),
    "400.html": (BAD_REQUEST, 400, FLAT),
    "401.html": (UNAUTHORIZED, 401, FLAT),
    "403.html": (FORBIDDEN, 403, FLAT),
}

DEFAULTS = dict(label_class="", script="")


def main():
    template = Template((ROOT / "template.html").read_text(encoding="utf-8"))
    for name, (page, quote, slope) in PAGES.items():
        html = template.substitute({**DEFAULTS, **page, "quote": quote, "slope": slope})
        (ROOT / name).write_text(html, encoding="utf-8")
        print(f"built {name}")


if __name__ == "__main__":
    main()
