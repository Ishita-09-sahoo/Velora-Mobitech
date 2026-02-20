function excelParser() {
  const workbook = read(buffer, { type: 'buffer' });
  const sheetName = workbook.SheetNames[0];
  const sheet = workbook.Sheets[sheetName];
  return utils.sheet_to_json(sheet);
}

export default excelParser;