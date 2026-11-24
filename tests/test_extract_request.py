"""The extraction request is the exact (file, ticker, range) set: no DB needed."""
from datetime import date

from proto_pair.experiments.extract import build_request


def test_request_scopes_fields_tickers_and_warmup():
    vn30 = [(date(2022, 8, 1), 'ACB'), (date(2022, 8, 1), 'FPT')]
    fcc = [(date(2022, 7, 20), 'VN30F2207', 'VN30F1M'),
           (date(2022, 7, 21), 'VN30F2207', 'VN30F1M'),
           (date(2022, 8, 1), 'VN30F2208', 'VN30F1M'),
           (date(2022, 8, 2), 'VN30F2208', 'VN30F1M')]
    req = build_request(vn30, fcc, date(2022, 8, 1), date(2022, 8, 2))
    files = {e['file']: e['tickers'] for e in req['files']}
    assert set(files) == {f'quote_{f}.parquet' for f in (
        'close', 'open', 'max', 'min', 'ceil', 'floor', 'reference', 'dailyvolume', 'ticker')}
    # warm-up contract and the index level are read for close only
    assert 'VN30F2207' in files['quote_close.parquet'] and 'VN30' in files['quote_close.parquet']
    assert 'VN30F2207' not in files['quote_ceil.parquet'] and 'VN30' not in files['quote_ceil.parquet']
    assert files['quote_ceil.parquet']['ACB'] == [['2022-08-01', '2022-08-03']]
    assert files['quote_close.parquet']['VN30'] == [['2022-07-20', '2022-08-03']]
    assert set(files['quote_ticker.parquet']) == {'ACB', 'FPT', 'VN30', 'VN30F2207', 'VN30F2208'}
