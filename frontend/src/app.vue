<style>
  html {
    font-size: 16px;
  }

  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans',
      'Droid Sans', 'Helvetica Neue', 'Microsoft Yahei', sans-serif;
  }

  body * {
    box-sizing: border-box;
    flex-shrink: 0;
  }

  #app {
    width: 100vw;
    height: 100vh;
  }

  .flex-row {
    display: flex;
    flex-direction: row;
  }

  .flex-col {
    display: flex;
    flex-direction: column;
  }

  .justify-start {
    justify-content: flex-start;
  }

  .justify-end {
    justify-content: flex-end;
  }

  .justify-center {
    justify-content: center;
  }

  .justify-between {
    justify-content: space-between;
  }

  .justify-around {
    justify-content: space-around;
  }

  .justify-evenly {
    justify-content: space-evenly;
  }

  .items-start {
    align-items: flex-start;
  }

  .items-end {
    align-items: flex-end;
  }

  .items-center {
    align-items: center;
  }

  .items-baseline {
    align-items: baseline;
  }

  .items-stretch {
    align-items: stretch;
  }

  .self-start {
    align-self: flex-start;
  }

  .self-end {
    align-self: flex-end;
  }

  .self-center {
    align-self: center;
  }

  .self-baseline {
    align-self: baseline;
  }

  .self-stretch {
    align-self: stretch;
  }

  .flex-1 {
    flex: 1 1 0%;
  }

  .flex-auto {
    flex: 1 1 auto;
  }

  .grow {
    flex-grow: 1;
  }

  .grow-0 {
    flex-grow: 0;
  }

  .shrink {
    flex-shrink: 1;
  }

  .shrink-0 {
    flex-shrink: 0;
  }

  .relative {
    position: relative;
  }

  .ml-2 {
    margin-left: 2px;
  }

  .mt-2 {
    margin-top: 2px;
  }

  .ml-4 {
    margin-left: 4px;
  }

  .mt-4 {
    margin-top: 4px;
  }

  .ml-6 {
    margin-left: 6px;
  }

  .mt-6 {
    margin-top: 6px;
  }

  .ml-8 {
    margin-left: 8px;
  }

  .mt-8 {
    margin-top: 8px;
  }

  .ml-10 {
    margin-left: 10px;
  }

  .mt-10 {
    margin-top: 10px;
  }

  .ml-12 {
    margin-left: 12px;
  }

  .mt-12 {
    margin-top: 12px;
  }

  .ml-14 {
    margin-left: 14px;
  }

  .mt-14 {
    margin-top: 14px;
  }

  .ml-16 {
    margin-left: 16px;
  }

  .mt-16 {
    margin-top: 16px;
  }

  .ml-18 {
    margin-left: 18px;
  }

  .mt-18 {
    margin-top: 18px;
  }

  .ml-20 {
    margin-left: 20px;
  }

  .mt-20 {
    margin-top: 20px;
  }

  .ml-22 {
    margin-left: 22px;
  }

  .mt-22 {
    margin-top: 22px;
  }

  .ml-24 {
    margin-left: 24px;
  }

  .mt-24 {
    margin-top: 24px;
  }

  .ml-26 {
    margin-left: 26px;
  }

  .mt-26 {
    margin-top: 26px;
  }

  .ml-28 {
    margin-left: 28px;
  }

  .mt-28 {
    margin-top: 28px;
  }

  .ml-30 {
    margin-left: 30px;
  }

  .mt-30 {
    margin-top: 30px;
  }

  .ml-32 {
    margin-left: 32px;
  }

  .mt-32 {
    margin-top: 32px;
  }

  .ml-34 {
    margin-left: 34px;
  }

  .mt-34 {
    margin-top: 34px;
  }

  .ml-36 {
    margin-left: 36px;
  }

  .mt-36 {
    margin-top: 36px;
  }

  .ml-38 {
    margin-left: 38px;
  }

  .mt-38 {
    margin-top: 38px;
  }

  .ml-40 {
    margin-left: 40px;
  }

  .mt-40 {
    margin-top: 40px;
  }

  .ml-42 {
    margin-left: 42px;
  }

  .mt-42 {
    margin-top: 42px;
  }

  .ml-44 {
    margin-left: 44px;
  }

  .mt-44 {
    margin-top: 44px;
  }

  .ml-46 {
    margin-left: 46px;
  }

  .mt-46 {
    margin-top: 46px;
  }

  .ml-48 {
    margin-left: 48px;
  }

  .mt-48 {
    margin-top: 48px;
  }

  .ml-50 {
    margin-left: 50px;
  }

  .mt-50 {
    margin-top: 50px;
  }

  .ml-52 {
    margin-left: 52px;
  }

  .mt-52 {
    margin-top: 52px;
  }

  .ml-54 {
    margin-left: 54px;
  }

  .mt-54 {
    margin-top: 54px;
  }

  .ml-56 {
    margin-left: 56px;
  }

  .mt-56 {
    margin-top: 56px;
  }

  .ml-58 {
    margin-left: 58px;
  }

  .mt-58 {
    margin-top: 58px;
  }

  .ml-60 {
    margin-left: 60px;
  }

  .mt-60 {
    margin-top: 60px;
  }

  .ml-62 {
    margin-left: 62px;
  }

  .mt-62 {
    margin-top: 62px;
  }

  .ml-64 {
    margin-left: 64px;
  }

  .mt-64 {
    margin-top: 64px;
  }

  .ml-66 {
    margin-left: 66px;
  }

  .mt-66 {
    margin-top: 66px;
  }

  .ml-68 {
    margin-left: 68px;
  }

  .mt-68 {
    margin-top: 68px;
  }

  .ml-70 {
    margin-left: 70px;
  }

  .mt-70 {
    margin-top: 70px;
  }

  .ml-72 {
    margin-left: 72px;
  }

  .mt-72 {
    margin-top: 72px;
  }

  .ml-74 {
    margin-left: 74px;
  }

  .mt-74 {
    margin-top: 74px;
  }

  .ml-76 {
    margin-left: 76px;
  }

  .mt-76 {
    margin-top: 76px;
  }

  .ml-78 {
    margin-left: 78px;
  }

  .mt-78 {
    margin-top: 78px;
  }

  .ml-80 {
    margin-left: 80px;
  }

  .mt-80 {
    margin-top: 80px;
  }

  .ml-82 {
    margin-left: 82px;
  }

  .mt-82 {
    margin-top: 82px;
  }

  .ml-84 {
    margin-left: 84px;
  }

  .mt-84 {
    margin-top: 84px;
  }

  .ml-86 {
    margin-left: 86px;
  }

  .mt-86 {
    margin-top: 86px;
  }

  .ml-88 {
    margin-left: 88px;
  }

  .mt-88 {
    margin-top: 88px;
  }

  .ml-90 {
    margin-left: 90px;
  }

  .mt-90 {
    margin-top: 90px;
  }

  .ml-92 {
    margin-left: 92px;
  }

  .mt-92 {
    margin-top: 92px;
  }

  .ml-94 {
    margin-left: 94px;
  }

  .mt-94 {
    margin-top: 94px;
  }

  .ml-96 {
    margin-left: 96px;
  }

  .mt-96 {
    margin-top: 96px;
  }

  .ml-98 {
    margin-left: 98px;
  }

  .mt-98 {
    margin-top: 98px;
  }

  .ml-100 {
    margin-left: 100px;
  }

  .mt-100 {
    margin-top: 100px;
  }
</style>

<template>
  <div id="app">
    <router-view />
  </div>
</template>

