from django.core.management.base import BaseCommand
from funds.models import Fund


class Command(BaseCommand):
    help = 'Load mock Israeli mutual fund data'

    def handle(self, *args, **kwargs):
        # Clear existing funds
        Fund.objects.all().delete()

        # Mock data based on Israeli mutual funds
        mock_funds = [
            # מיטב דש
            {'name': 'מיטב נעמה מנייתי', 'company': 'מיטב דש', 'category': 'STOCKS', 'return_rate': 12.5},
            {'name': 'מיטב אג"ח ממשלתי', 'company': 'מיטב דש', 'category': 'BONDS', 'return_rate': 3.8},
            {'name': 'מיטב מדד ת"א 35', 'company': 'מיטב דש', 'category': 'INDEX', 'return_rate': 15.2},
            {'name': 'מיטב שוק כסף', 'company': 'מיטב דש', 'category': 'MONEY_MARKET', 'return_rate': 2.1},

            # הלמן אלדובי
            {'name': 'הלמן אלדובי מניות ישראל', 'company': 'הלמן אלדובי', 'category': 'STOCKS', 'return_rate': 14.8},
            {'name': 'הלמן אלדובי אג"ח קונצרני', 'company': 'הלמן אלדובי', 'category': 'BONDS', 'return_rate': 4.2},
            {'name': 'הלמן אלדובי מעורב', 'company': 'הלמן אלדובי', 'category': 'MIXED', 'return_rate': 8.5},
            {'name': 'הלמן אלדובי נדל"ן', 'company': 'הלמן אלדובי', 'category': 'REAL_ESTATE', 'return_rate': 6.7},

            # כלל
            {'name': 'כלל מניות ישראל', 'company': 'כלל', 'category': 'STOCKS', 'return_rate': 13.2},
            {'name': 'כלל אג"ח', 'company': 'כלל', 'category': 'BONDS', 'return_rate': 3.5},
            {'name': 'כלל מדד S&P 500', 'company': 'כלל', 'category': 'FOREIGN', 'return_rate': 18.9},
            {'name': 'כלל שוק כסף', 'company': 'כלל', 'category': 'MONEY_MARKET', 'return_rate': 2.3},

            # אנליסט
            {'name': 'אנליסט מניות ישראל', 'company': 'אנליסט', 'category': 'STOCKS', 'return_rate': 11.8},
            {'name': 'אנליסט אג"ח ממשלתי', 'company': 'אנליסט', 'category': 'BONDS', 'return_rate': 3.9},
            {'name': 'אנליסט מעורב', 'company': 'אנליסט', 'category': 'MIXED', 'return_rate': 7.6},
            {'name': 'אנליסט חו"ל', 'company': 'אנליסט', 'category': 'FOREIGN', 'return_rate': 16.4},

            # מור
            {'name': 'מור מניות ישראל', 'company': 'מור', 'category': 'STOCKS', 'return_rate': 10.9},
            {'name': 'מור אג"ח קונצרני', 'company': 'מור', 'category': 'BONDS', 'return_rate': 4.1},
            {'name': 'מור מדד נאסד"ק', 'company': 'מור', 'category': 'FOREIGN', 'return_rate': 22.3},
            {'name': 'מור נדל"ן', 'company': 'מור', 'category': 'REAL_ESTATE', 'return_rate': 5.8},

            # פסגות
            {'name': 'פסגות מניות ישראל', 'company': 'פסגות', 'category': 'STOCKS', 'return_rate': 12.7},
            {'name': 'פסגות אג"ח', 'company': 'פסגות', 'category': 'BONDS', 'return_rate': 3.7},
            {'name': 'פסגות מעורב', 'company': 'פסגות', 'category': 'MIXED', 'return_rate': 8.2},
            {'name': 'פסגות שוק כסף', 'company': 'פסגות', 'category': 'MONEY_MARKET', 'return_rate': 2.0},

            # פניקס
            {'name': 'פניקס מניות ישראל', 'company': 'פניקס', 'category': 'STOCKS', 'return_rate': 13.8},
            {'name': 'פניקס אג"ח ממשלתי', 'company': 'פניקס', 'category': 'BONDS', 'return_rate': 4.0},
            {'name': 'פניקס מדד ת"א 125', 'company': 'פניקס', 'category': 'INDEX', 'return_rate': 14.5},
            {'name': 'פניקס חו"ל', 'company': 'פניקס', 'category': 'FOREIGN', 'return_rate': 17.8},

            # הראל
            {'name': 'הראל מניות ישראל', 'company': 'הראל', 'category': 'STOCKS', 'return_rate': 11.5},
            {'name': 'הראל אג"ח קונצרני', 'company': 'הראל', 'category': 'BONDS', 'return_rate': 3.6},
            {'name': 'הראל מעורב', 'company': 'הראל', 'category': 'MIXED', 'return_rate': 7.9},
            {'name': 'הראל נדל"ן', 'company': 'הראל', 'category': 'REAL_ESTATE', 'return_rate': 6.2},

            # מנורה מבטחים
            {'name': 'מנורה מניות ישראל', 'company': 'מנורה מבטחים', 'category': 'STOCKS', 'return_rate': 12.1},
            {'name': 'מנורה אג"ח', 'company': 'מנורה מבטחים', 'category': 'BONDS', 'return_rate': 3.8},
            {'name': 'מנורה מדד S&P 500', 'company': 'מנורה מבטחים', 'category': 'FOREIGN', 'return_rate': 19.5},
            {'name': 'מנורה שוק כסף', 'company': 'מנורה מבטחים', 'category': 'MONEY_MARKET', 'return_rate': 2.2},

            # אקסלנס
            {'name': 'אקסלנס מניות ישראל', 'company': 'אקסלנס', 'category': 'STOCKS', 'return_rate': 10.6},
            {'name': 'אקסלנס אג"ח ממשלתי', 'company': 'אקסלנס', 'category': 'BONDS', 'return_rate': 3.4},
            {'name': 'אקסלנס מעורב', 'company': 'אקסלנס', 'category': 'MIXED', 'return_rate': 7.3},
            {'name': 'אקסלנס חו"ל', 'company': 'אקסלנס', 'category': 'FOREIGN', 'return_rate': 15.9},
        ]

        created_count = 0
        for fund_data in mock_funds:
            Fund.objects.create(**fund_data)
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} mock funds')
        )
