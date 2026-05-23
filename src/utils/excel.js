import * as XLSX from 'xlsx'

function readFileAsArrayBuffer(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => resolve(new Uint8Array(e.target.result))
    reader.onerror = () => reject(new Error('文件读取失败'))
    reader.readAsArrayBuffer(file)
  })
}

export async function readExcel(file) {
  const data = await readFileAsArrayBuffer(file)
  const workbook = XLSX.read(data, { type: 'array' })

  const sheets = workbook.SheetNames.map((name) => {
    const sheet = workbook.Sheets[name]
    const range = XLSX.utils.decode_range(sheet['!ref'] || 'A1')
    const allRows = []

    for (let r = range.s.r; r <= range.e.r; r++) {
      const row = []
      for (let c = range.s.c; c <= range.e.c; c++) {
        const addr = XLSX.utils.encode_cell({ r, c })
        const cell = sheet[addr]
        row.push(cell ? String(cell.v ?? '') : '')
      }
      allRows.push(row)
    }

    return { name, rows: JSON.parse(JSON.stringify(allRows)) }
  })

  return JSON.parse(JSON.stringify({ fileName: file.name, fileSize: file.size, sheets }))
}

export async function exportResults(results, displayCol, title) {
  const XLSX = await import('xlsx')

  const header = ['#', `${displayCol} 列数据`, '原始行号', '类型', '识别到的值', '原文内容', '风险类型']
  const data = results.map((r, i) => [
    i + 1,
    r.displayValue,
    r.rowNum,
    r.dataType,
    r.dataType === '电话' ? r.phones.join(', ') : r.sns.join(', '),
    r.originalText,
    r.riskLevel,
  ])

  const ws = XLSX.utils.aoa_to_sheet([header, ...data])
  ws['!cols'] = [
    { wch: 6 },
    { wch: 20 },
    { wch: 10 },
    { wch: 8 },
    { wch: 24 },
    { wch: 60 },
    { wch: 10 },
  ]

  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '识别结果')
  XLSX.writeFile(wb, `${title}.xlsx`)
}
