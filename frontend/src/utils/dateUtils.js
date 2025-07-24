/**
 * 格式化日期以供显示。
 * 将年份和月份组合成“YYYY年MM月”或“YYYY年”的格式。
 *
 * @param {number|string} year - 年份。
 * @param {number|string} month - 月份。
 * @returns {string} 格式化后的日期字符串。
 */
export function formatDateForDisplay(year, month) {
  if (!year && !month) return '';
  const formattedMonth = month
    ? parseInt(month).toString().padStart(2, '0')
    : '';
  if (year && formattedMonth) {
    return `${year}年${formattedMonth}月`;
  } else if (year) {
    return `${year}年`;
  } else {
    return '无日期';
  }
}
