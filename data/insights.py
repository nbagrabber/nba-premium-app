import os
from typing import List
import feedparser
import logging
import asyncio
import aiohttp
import urllib.parse
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
from engine.internal_logger import internal_logger
from .scrapers.bsky_scraper import bsky_instance

load_dotenv()

logger = logging.getLogger(__name__)

import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
]

def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/"
    }

async def fetch_rss(session, url, limit=10):
    """Unified RSS fetcher with User-Agent and individual timeout."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as response:
            if response.status != 200:
                logger.warning(f"[fetch-rss] HTTP {response.status} for {url}")
                return []
            xml_content = await response.text()
            # Интегрируем feedparser в асинхронный поток
            feed = await asyncio.to_thread(feedparser.parse, xml_content)
            return feed.entries[:limit]
    except Exception as e:
        logger.error(f"[fetch-rss] Error fetching {url}: {e}")
        return []

async def get_reddit_insights(session: aiohttp.ClientSession, team_name: str, limit: int = 5) -> list[str]:
    """Сбор горячих тем из Reddit (Parallel)."""
    subreddit_map = {
        "lakers": "lakers", "nuggets": "denvernuggets", "warriors": "warriors",
        "celtics": "bostonceltics", "bucks": "mkeebucks", "suns": "suns",
        "clippers": "laclippers", "mavericks": "mavericks", "76ers": "sixers",
        "heat": "heat", "knicks": "nyknicks", "bulls": "chicagobulls",
        "grizzlies": "memphisgrizzlies", "kings": "kings", "thunder": "thunder",
        "wolves": "timberwolves", "pelicans": "nolapelicans", "rockets": "rockets",
        "spurs": "nbaspurs", "blazers": "ripcity", "jazz": "utahjazz",
        "hawks": "atlantahawks", "nets": "gonets", "hornets": "charlottehornets",
        "pacers": "pacers", "pistons": "detroitpistons", "magic": "orlandomagic",
        "raptors": "torontoraptors", "wizards": "washingtonwizards",
        "cavs": "clevelandcavs"
    }
    
    team_slug = team_name.lower().split()[-1]
    sub = subreddit_map.get(team_slug, "nba")
    encoded_team = urllib.parse.quote(team_name)
    
    urls = [
        f"https://www.reddit.com/r/nba/search/.rss?q={encoded_team}&sort=hot&t=day",
        f"https://www.reddit.com/r/{sub}/hot/.rss",
        f"https://www.reddit.com/r/NBA_Draft/search/.rss?q={encoded_team}&sort=new&t=week"
    ]
    
    tasks = [fetch_rss(session, url, limit) for url in urls]
    results = await asyncio.gather(*tasks)
    
    insights = []
    for entries in results:
        for entry in entries:
            title = re.sub('<[^<]+?>', '', entry.title)
            insights.append(f"Reddit: {title}\nLink: {entry.link}")
            
    if insights:
        await internal_logger.log(f"Reddit: Total found {len(insights)} entries for {team_name}")
    return insights

async def get_rss_news(session: aiohttp.ClientSession, team_names: list[str] = None) -> dict[str, list[str]]:
    """Сбор новостей из источников (Parallel)."""
    feeds = {
        "Group 1: Journalism & Insights": [
            "https://www.espn.com/espn/rss/nba/news",
            "https://www.cbssports.com/rss/headlines/nba/",
            "https://hoopshype.com/rss/",
            "https://bleacherreport.com/articles/feed?tag_id=nba",
            "https://sports.yahoo.com/nba/rss",
            "https://www.yardbarker.com/rss/sport/1"
        ],
        "Group 2: Injuries & Roster": [
            "https://www.rotowire.com/rss/news.php?sport=NBA",
            "https://basketball.realgm.com/rss/wiretap/0/0.xml",
            "https://www.cbssports.com/rss/headlines/nba/",
            "https://www.yardbarker.com/rss/sport/1",
            "https://fansided.com/feed/"
        ],
        "Group 3: Advanced Analytics": [
            "https://basketball.realgm.com/rss/wiretap/0/0.xml",
            "https://www.nbastuffer.com/feed/",
            "https://www.basketball-reference.com/blog/?feed=rss2",
            "https://cleaningtheglass.com/articles/feed/",
            "https://www.viziball.com/rss",
            "https://stathead.com/feed/",
            "https://www.pbpstats.com/feed/"
        ],
        "Group 4: Market & Trends": [
            "https://www.actionnetwork.com/nba/feed",
            "https://www.hoopsrumors.com/feed/",
            "https://www.pickswise.com/nba/feed/"
        ],
        "Group 5: X Insiders (High Speed)": [
            "https://www.hoopsrumors.com/feed/",
            "https://hoopshype.com/rss/",
            "https://basketball.realgm.com/rss/wiretap/0/0.xml"
        ],
        "Group 6: Local Beat Insights": [
            "https://www.rotowire.com/rss/news.php?sport=NBA",
            "https://hoopshype.com/rumors/rss/",
            "https://marcstein.substack.com/feed",
            "https://www.nbcsportsedge.com/rss/articles"
        ]
    }
    
    # Веса надежности источников (1-10)
    SOURCE_WEIGHTS = {
        "Group 1: Journalism & Insights": 7,
        "Group 2: Injuries & Roster": 10,
        "Group 3: Advanced Analytics": 8,
        "Group 4: Market & Trends": 8,
        "Group 5: X Insiders (High Speed)": 10,
        "Group 6: Local Beat Insights": 9,
        "Reddit": 4,
        "NBA Official L2M": 6
    }
    
    # SB Nation Team Blogs mapping
    TEAM_BLOGS = {
        "hawks": "peachtreehoops.com", "celtics": "celticsblog.com", "nets": "netsdaily.com",
        "hornets": "atthehive.com", "bulls": "blogabull.com", "cavs": "fearthesword.com",
        "mavericks": "mavsmoneyball.com", "nuggets": "denverstiffs.com", "pistons": "badboysball.com",
        "warriors": "goldenstateofmind.com", "rockets": "thedreamshake.com", "pacers": "indycornrows.com",
        "clippers": "clipsnation.com", "lakers": "silverscreenandroll.com", "grizzlies": "grizzlybearblues.com",
        "heat": "hothothoops.com", "bucks": "brewhoop.com", "wolves": "canishoopus.com",
        "pelicans": "thebirdwrites.com", "knicks": "postingandtoasting.com", "thunder": "welcometoloudcity.com",
        "magic": "orlandopinstripedpost.com", "76ers": "libertyballers.com", "suns": "brightsideofthesun.com",
        "blazers": "blazersedge.com",        "kings": "kingsherald.com", "spurs": "poundingtherock.com",
        "raptors": "raptorshq.com", "jazz": "slcdunk.com", "wizards": "bulletsforever.com"
    }
    
    # Добавляем местные блоги в Group 1 динамически
    if team_names:
        for team_name in team_names:
            slug = team_name.lower().split()[-1]
            if slug in TEAM_BLOGS:
                blog_domain = TEAM_BLOGS[slug]
                feeds["Group 6: Local Beat Insights"].append(f"https://www.{blog_domain}/feed/")

    keywords = ["preview", "prediction", "matchup", "injury", "out", "lineup", "shams", "woj", "insider", "report", 
                "sidelined", "rest", "load management", "illness", "personal reasons", "questionable", "doubtful",
                "pace", "efficiency", "rating", "stat", "analytics", "viziball", "ctg", "cleaning the glass", 
                "net rating", "defensive", "offensive", "possessions"]
    if team_names:
        for name in team_names:
            keywords.append(name.lower())
            parts = name.lower().split()
            if parts: keywords.append(parts[-1])
    
    # [ANTI-STALE] Dynamic date check: Current day only
    target_date = datetime.now().date()
    now = datetime.now()
    results = {}
    
    # Семафор для ограничения одновременных запросов (макс 1 одновременно)
    semaphore = asyncio.Semaphore(1)
    
    async def sem_fetch(group, url):
        import random
        # Специфично для Группы 3: ставим time.sleep(5) перед парсингом для загрузки/паузы
        if group == "Group 3: Advanced Analytics":
            logger.info(f"[fetch-rss] Group 3 Advanced Analytics triggered for {url}. Waiting 5s...")
            await asyncio.sleep(5)

        # Увеличенная пауза для 100% стабильности (5-15 секунд между запросами)
        await asyncio.sleep(random.uniform(5.0, 15.0))
        async with semaphore:
            return await fetch_rss(session, url, 30)
            
    # Собираем все URLы для параллельной загрузки
    all_tasks = []
    group_mapping = []
    for group, urls in feeds.items():
        if group not in results: results[group] = []
        for url in urls:
            all_tasks.append(sem_fetch(group, url))
            group_mapping.append(group)
            
    all_results = await asyncio.gather(*all_tasks)
    
    for entries, group in zip(all_results, group_mapping):
        weight = SOURCE_WEIGHTS.get(group, 5)
        for entry in entries:
            # [ANTI-STALE] Expanded window: Last 3 days to capture previews
            is_fresh = False
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                import time
                dt_published = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                # Разрешаем новости за последние 3 дня (для аналитики и инсайдов - 7 дней)
                allowed_days = 7 if group in ["Group 3: Advanced Analytics", "Group 6: Local Beat Insights"] else 3
                if dt_published.date() >= (target_date - timedelta(days=allowed_days)):
                    is_fresh = True
                else:
                    logger.debug(f"[anti-stale] Skipping old report from {dt_published.date()}")
            
            if not is_fresh: continue

            title = entry.title
            summary = entry.get('summary', '')[:500]
            content = f"[{group}] (Reliability: {weight}/10) Title: {title}\nSummary: {summary}"
            
            if any(kw in content.lower() for kw in keywords):
                results[group].append(content)
                
    # Лимит на группу (увеличим для более глубокого анализа)
    for g in results:
        results[g] = results[g][:30] # Было 12
            
    return results

async def get_bsky_insights(team_names: List[str] = None) -> List[str]:
    """Сбор инсайдов из Bluesky (Shams, Underdog, etc)."""
    handles = [
        "shamsbot.bsky.social", 
        "underdognba.bsky.social", 
        "thesteinline.bsky.social", 
        "nba.com",
        "warriorsbot.bsky.social"
    ]
    
    # Ключевые слова из ТЗ
    keywords = ["BREAKING", "OUT", "QUESTIONABLE", "GTD", "AVAILABLE", "Sidelined"]
    if team_names:
        keywords.extend([t.lower() for t in team_names])
    
    try:
        # Проверяем триггеры (посты с ключами)
        alerts = await bsky_instance.check_triggers(handles, keywords)
        
        insights = []
        for a in alerts:
            # Сжатый формат: только текст и время
            insights.append(f"[Bluesky] {a['author']} ({a['created_at']}): {a['text']}")
        
        if insights:
            await internal_logger.log(f"Bluesky: Found {len(insights)} relevant alerts.")
        return insights
    except Exception as e:
        logger.error(f"[BSky-Insights] Error: {e}")
        return []

async def collect_match_context(home_team: str, away_team: str) -> dict[str, str]:
    """Сбор контекста с глобальным таймаутом и параллелизацией."""
    sources = {}
    
    async with aiohttp.ClientSession(headers=get_random_headers()) as session:
        try:
            from .scrapers.l2m_scraper import L2MScraper
            l2m_scraper = L2MScraper()
            
            # Запускаем сбор Reddit, RSS и L2M параллельно с общим таймаутом
            reddit_task_home = get_reddit_insights(session, home_team)
            reddit_task_away = get_reddit_insights(session, away_team)
            news_task = get_rss_news(session, [home_team, away_team])
            l2m_task = l2m_scraper.get_recent_reports()
            bsky_task = get_bsky_insights([home_team, away_team])
            
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(reddit_task_home, reddit_task_away, news_task, l2m_task, bsky_task),
                    timeout=90
                )
                
                home_reddit, away_reddit, news_data, l2m_data, bsky_data = results
                
                # Веса
                REDDIT_WEIGHT = 4
                L2M_WEIGHT = 6
                
                if home_reddit: 
                    sources[f"Social Context: {home_team}"] = f"[Reddit] (Reliability: {REDDIT_WEIGHT}/10)\n" + "\n\n".join(home_reddit)
                if away_reddit: 
                    sources[f"Social Context: {away_team}"] = f"[Reddit] (Reliability: {REDDIT_WEIGHT}/10)\n" + "\n\n".join(away_reddit)
                
                await internal_logger.log(f"Scraper: Collecting Advanced Intelligence for {home_team} vs {away_team}...")
                
                # Обеспечиваем, что все 6 групп есть в логе
                required_groups = [
                    "Group 1: Journalism & Insights",
                    "Group 2: Injuries & Roster",
                    "Group 3: Advanced Analytics",
                    "Group 4: Market & Trends",
                    "Group 5: X Insiders (High Speed)",
                    "Group 6: Local Beat Insights"
                ]
                
                for group in required_groups:
                    items = news_data.get(group, [])
                    if items:
                        sources[group] = "\n\n---\n\n".join(items)
                    await internal_logger.log(f"Scraper: Found {len(items)} relevant items in {group}")
                
                if bsky_data:
                    sources["Bluesky Insiders"] = "\n\n---\n\n".join(bsky_data)

                if l2m_data:
                    sources["Referee L2M Reports"] = f"[NBA Official L2M] (Reliability: {L2M_WEIGHT}/10)\n" + l2m_data
            
            except asyncio.TimeoutError:
                logger.warning(f"[collect-context] Timeout getting context for {home_team} vs {away_team}")
                await internal_logger.log(f"⚠️ Scraper TIMEOUT for {away_team}@{home_team}. Returning partial data.", "WARNING")
                
        except Exception as e:
            logger.error(f"[collect-context] Fatal error in data collection: {e}")
            
    return sources
