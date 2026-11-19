const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();
for(const n of ['recto','verso']){
 const p=await b.newPage({viewport:{width:880,height:580},deviceScaleFactor:1039/880*2});
 await p.goto('file://'+__dirname+'/'+n+'.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(600);
 await p.screenshot({path:__dirname+'/carte_'+n+'_8.8x5.8cm.png'});await p.close();}
await b.close();})();
