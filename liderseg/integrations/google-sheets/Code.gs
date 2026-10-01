function doPost(e) {
  const reply = (ok) => ContentService.createTextOutput(JSON.stringify({ ok })).setMimeType(ContentService.MimeType.JSON);
  let lock;
  try {
    const settings = PropertiesService.getScriptProperties();
    const secret = settings.getProperty('CONTACT_SECRET');
    const data = JSON.parse(e.postData.contents);
    if (!secret || secret.length < 32 || data.secret !== secret) return reply(false);
    if (typeof data.name !== 'string' || data.name.trim().length < 2 || data.name.length > 100 || /[\x00-\x1F]/.test(data.name) || !/^[1-9]{2}9\d{8}$/.test(data.whatsapp) || !/^[a-f0-9-]{36}$/i.test(data.submission_id)) return reply(false);
    lock = LockService.getScriptLock();
    lock.waitLock(15000);
    const sheet = SpreadsheetApp.openById(settings.getProperty('SPREADSHEET_ID')).getSheetByName('Contatos');
    if (!sheet) return reply(false);
    // Um reenvio após timeout não cria uma segunda linha.
    const last = sheet.getLastRow();
    if (last > 1 && sheet.getRange(2, 4, last - 1, 1).createTextFinder(data.submission_id).matchEntireCell(true).findNext()) return reply(true);
    const row = Math.max(last + 1, 2);
    sheet.getRange(row, 2, 1, 3).setNumberFormat('@');
    // Prefixo de texto impede que nomes sejam interpretados como fórmulas.
    sheet.getRange(row, 1, 1, 4).setValues([[new Date(), "'" + data.name.trim(), "'" + data.whatsapp, data.submission_id]]);
    SpreadsheetApp.flush();
    return reply(true);
  } catch (_) {
    return reply(false);
  } finally {
    if (lock && lock.hasLock()) lock.releaseLock();
  }
}
