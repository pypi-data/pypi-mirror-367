def to_gsheet(data, client, spreadsheet_id, sheet, row='new', expand_columns=False, cols=None,truncate=True):
    wb = client.open_by_key(spreadsheet_id)
    try:
        if row == 'new':
            sheetdata = wb.worksheet(sheet).get_all_values()
            header = sheetdata[0]
            row_num = max(len(sheetdata) + 1,2)
        else:
            header = wb.worksheet(sheet).row_values(1)
            row_num = int(row)
            if truncate:
                wb.values_clear(f"'{sheet}'!{row_num}:1000000")
        data_header = []
        if data:
            if hasattr(data, 'header'):
                data = data.list()
            if cols:
                data_header = cols
            elif isinstance(data[0], dict):
                data_header = data[0].keys()
            else:
                data_header = data[0]
        new_header = header.copy()
        if expand_columns:
            new_header.extend([x for x in data_header if x not in header])
        data = petl.cat(data, header=new_header).list()
        # Write data to shet
        wb.worksheet(sheet).update(data[1:], f'A{row_num}')
        if new_header != header:
            wb.worksheet(sheet).update([new_header], 'A1')
        return True
    except Exception as e:
        print(e)
        return False