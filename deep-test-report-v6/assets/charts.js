(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();
  var success = style.getPropertyValue('--success').trim();
  var warn = style.getPropertyValue('--warn').trim();
  var danger = style.getPropertyValue('--danger').trim();

  // --- Chart 1: 各测试类别通过率 ---
  var chart1 = echarts.init(document.getElementById('chart-category'), null, { renderer: 'svg' });
  chart1.setOption({
    animation: false,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, appendToBody: true },
    legend: { data: ['通过', '部分通过', '失败'], top: 0, textStyle: { color: muted, fontSize: 12 } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['回归验证', '已训练问题', '新数据集', '未训练问题', '压力测试'],
      axisLabel: { color: ink, fontSize: 11, interval: 0 },
      axisLine: { lineStyle: { color: rule } },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      max: 90,
      axisLabel: { color: muted, fontSize: 11 },
      splitLine: { lineStyle: { color: rule, type: 'dashed' } },
      axisLine: { show: false }
    },
    series: [
      {
        name: '通过',
        type: 'bar',
        stack: 'total',
        data: [13, 17, 79, 55, 5],
        itemStyle: { color: success, borderRadius: [0, 0, 0, 0] },
        barWidth: '40%'
      },
      {
        name: '部分通过',
        type: 'bar',
        stack: 'total',
        data: [0, 0, 2, 0, 1],
        itemStyle: { color: warn },
        barWidth: '40%'
      },
      {
        name: '失败',
        type: 'bar',
        stack: 'total',
        data: [0, 0, 0, 0, 0],
        itemStyle: { color: danger },
        barWidth: '40%'
      }
    ]
  });
  window.addEventListener('resize', function() { chart1.resize(); });

  // --- Chart 2: 修复前 vs 修复后 ---
  var chart2 = echarts.init(document.getElementById('chart-fix'), null, { renderer: 'svg' });
  chart2.setOption({
    animation: false,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, appendToBody: true },
    legend: { data: ['修复前得分', '修复后得分'], top: 0, textStyle: { color: muted, fontSize: 12 } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['售价低于20万的车型', '完播率低于30%的剧', '贵州茅台的收盘价'],
      axisLabel: { color: ink, fontSize: 10, interval: 0, rotate: 10 },
      axisLine: { lineStyle: { color: rule } },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: { color: muted, fontSize: 11, formatter: '{value}%' },
      splitLine: { lineStyle: { color: rule, type: 'dashed' } },
      axisLine: { show: false }
    },
    series: [
      {
        name: '修复前得分',
        type: 'bar',
        data: [75, 75, 60],
        itemStyle: { color: warn, borderRadius: [4, 4, 0, 0] },
        barWidth: '30%'
      },
      {
        name: '修复后得分',
        type: 'bar',
        data: [100, 100, 100],
        itemStyle: { color: success, borderRadius: [4, 4, 0, 0] },
        barWidth: '30%'
      }
    ]
  });
  window.addEventListener('resize', function() { chart2.resize(); });

  // --- Chart 3: 新数据集各类型测试通过率 ---
  var chart3 = echarts.init(document.getElementById('chart-newds'), null, { renderer: 'svg' });
  chart3.setOption({
    animation: false,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, appendToBody: true },
    legend: { data: ['新能源汽车', '咖啡门店', '流媒体平台'], top: 0, textStyle: { color: muted, fontSize: 12 } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['summary', 'ranking', 'trend', 'compare', 'distribution', 'pct', 'filter', 'extreme', 'multi-metric', 'correlation', 'groupby', 'count', 'complex'],
      axisLabel: { color: ink, fontSize: 9, interval: 0, rotate: 35 },
      axisLine: { lineStyle: { color: rule } },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      max: 105,
      axisLabel: { color: muted, fontSize: 11, formatter: '{value}%' },
      splitLine: { lineStyle: { color: rule, type: 'dashed' } },
      axisLine: { show: false }
    },
    series: [
      {
        name: '新能源汽车',
        type: 'bar',
        data: [100, 100, 100, 100, 100, 100, 0, 100, 100, 100, 100, 100, 100],
        itemStyle: { color: accent, borderRadius: [3, 3, 0, 0] },
        barWidth: '20%'
      },
      {
        name: '咖啡门店',
        type: 'bar',
        data: [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
        itemStyle: { color: accent2, borderRadius: [3, 3, 0, 0] },
        barWidth: '20%'
      },
      {
        name: '流媒体平台',
        type: 'bar',
        data: [100, 100, 100, 100, 100, 100, 0, 100, 100, 100, 100, 100, 100],
        itemStyle: { color: success, borderRadius: [3, 3, 0, 0] },
        barWidth: '20%'
      }
    ]
  });
  window.addEventListener('resize', function() { chart3.resize(); });

  // --- Chart 4: 修复项按严重度分布 ---
  var chart4 = echarts.init(document.getElementById('chart-severity'), null, { renderer: 'svg' });
  chart4.setOption({
    animation: false,
    tooltip: { trigger: 'item', appendToBody: true, formatter: '{b}: {c}项 ({d}%)' },
    legend: { orient: 'horizontal', bottom: 0, textStyle: { color: muted, fontSize: 12 } },
    series: [
      {
        type: 'pie',
        radius: ['35%', '60%'],
        center: ['50%', '45%'],
        data: [
          { value: 6, name: 'P0 - 严重', itemStyle: { color: danger } },
          { value: 11, name: 'P1 - 中等', itemStyle: { color: warn } },
          { value: 3, name: 'P2 - 轻微', itemStyle: { color: muted } }
        ],
        label: {
          color: ink,
          fontSize: 12,
          formatter: '{b}\n{c}项 ({d}%)'
        },
        labelLine: { lineStyle: { color: rule } }
      }
    ]
  });
  window.addEventListener('resize', function() { chart4.resize(); });
})();
