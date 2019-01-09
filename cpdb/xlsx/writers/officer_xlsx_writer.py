from openpyxl import Workbook


class OfficerXlsxWriter(object):
    def __init__(self, officer):
        self.officer = officer
        self.wb = Workbook()

    def write_sheet(self, ws, rows):
        if len(rows) > 0:
            for column_idx, column_name in enumerate(rows[0].keys()):
                ws.cell(row=1, column=column_idx + 1, value=column_name)

            for row_idx, row in enumerate(rows):
                for column_idx, value in enumerate(row.values()):
                    ws.cell(row=row_idx + 2, column=column_idx + 1, value=value)

    @property
    def file_name(self):
        raise NotImplementedError

    def export_xlsx(self):
        raise NotImplementedError

    def save(self):
        self.wb.remove(self.wb['Sheet'])
        self.wb.save(self.file_name)
