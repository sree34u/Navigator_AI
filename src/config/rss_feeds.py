"""Categorized production RSS feed URL constants for UPSC current affairs."""

from __future__ import annotations

from typing import Final

GOVERNMENT_FEEDS: Final[tuple[str, ...]] = (
    "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",
    "https://pib.gov.in/RssMain.aspx?ModId=3&Lang=1&Regid=3",
    "https://www.pib.gov.in/PressReleseDetail.aspx?rss=1",
    "https://sansad.in/rss/ls",
    "https://sansad.in/rss/rs",
    "https://www.mea.gov.in/rss-feeds.htm",
)

INTERNATIONAL_FEEDS: Final[tuple[str, ...]] = (
    "https://www.un.org/en/rss.xml",
    "https://www.state.gov/rss-feeds/",
    "https://www.reuters.com/world/rss",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
)

ECONOMY_FEEDS: Final[tuple[str, ...]] = (
    "https://www.rbi.org.in/Scripts/RssPressRelease.aspx",
    "https://www.livemint.com/rss/economy",
    "https://www.business-standard.com/rss/economy-policy-102.rss",
    "https://www.thehindubusinessline.com/economy/feeder/default.rss",
    "https://www.moneycontrol.com/rss/economy.xml",
)

SCIENCE_FEEDS: Final[tuple[str, ...]] = (
    "https://www.isro.gov.in/rss-feed",
    "https://www.thehindu.com/sci-tech/science/feeder/default.rss",
    "https://www.nature.com/nature.rss",
    "https://www.sciencedaily.com/rss/top/science.xml",
    "https://pib.gov.in/RssMain.aspx?ModId=8&Lang=1&Regid=3",
)

ENVIRONMENT_FEEDS: Final[tuple[str, ...]] = (
    "https://moef.gov.in/rss",
    "https://www.downtoearth.org.in/rss/environment",
    "https://unfccc.int/news/rss.xml",
    "https://www.iucn.org/rss.xml",
    "https://www.thehindu.com/sci-tech/energy-and-environment/feeder/default.rss",
)

SECURITY_FEEDS: Final[tuple[str, ...]] = (
    "https://www.mha.gov.in/rss.xml",
    "https://www.idsa.in/rss/publication",
    "https://pib.gov.in/RssMain.aspx?ModId=13&Lang=1&Regid=3",
    "https://www.thehindu.com/news/national/feeder/default.rss",
)

REPORTS_FEEDS: Final[tuple[str, ...]] = (
    "https://www.niti.gov.in/rss.xml",
    "https://www.worldbank.org/en/news/all.rss",
    "https://www.who.int/rss-feeds/news-english.xml",
    "https://www.imf.org/en/News/RSS?Language=ENG",
    "https://unesdoc.unesco.org/rss",
)

ALL_FEED_CATEGORIES: Final[dict[str, tuple[str, ...]]] = {
    "government": GOVERNMENT_FEEDS,
    "international": INTERNATIONAL_FEEDS,
    "economy": ECONOMY_FEEDS,
    "science": SCIENCE_FEEDS,
    "environment": ENVIRONMENT_FEEDS,
    "security": SECURITY_FEEDS,
    "reports": REPORTS_FEEDS,
}