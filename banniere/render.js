const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();
const p=await b.newPage({viewport:{width:1000,height:300},deviceScaleFactor:6});
await p.goto('file://'+__dirname+'/banniere.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
await p.screenshot({path:__dirname+'/banniere_100x30cm.png'});
await b.close();})();
