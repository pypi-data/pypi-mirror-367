"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[2524],{13130:(t,e,n)=>{n.d(e,{A:()=>d});const o=t=>"object"==typeof t&&null!=t&&1===t.nodeType,i=(t,e)=>(!e||"hidden"!==t)&&"visible"!==t&&"clip"!==t,r=(t,e)=>{if(t.clientHeight<t.scrollHeight||t.clientWidth<t.scrollWidth){const n=getComputedStyle(t,null);return i(n.overflowY,e)||i(n.overflowX,e)||(t=>{const e=(t=>{if(!t.ownerDocument||!t.ownerDocument.defaultView)return null;try{return t.ownerDocument.defaultView.frameElement}catch(t){return null}})(t);return!!e&&(e.clientHeight<t.scrollHeight||e.clientWidth<t.scrollWidth)})(t)}return!1},l=(t,e,n,o,i,r,l,a)=>r<t&&l>e||r>t&&l<e?0:r<=t&&a<=n||l>=e&&a>=n?r-t-o:l>e&&a<n||r<t&&a>n?l-e+i:0,a=t=>{const e=t.parentElement;return null==e?t.getRootNode().host||null:e},s=(t,e)=>{var n,i,s,c;if("undefined"==typeof document)return[];const{scrollMode:d,block:h,inline:p,boundary:u,skipOverflowHiddenElements:f}=e,m="function"==typeof u?u:t=>t!==u;if(!o(t))throw new TypeError("Invalid target");const g=document.scrollingElement||document.documentElement,v=[];let b=t;for(;o(b)&&m(b);){if(b=a(b),b===g){v.push(b);break}null!=b&&b===document.body&&r(b)&&!r(document.documentElement)||null!=b&&r(b,f)&&v.push(b)}const w=null!=(i=null==(n=window.visualViewport)?void 0:n.width)?i:innerWidth,F=null!=(c=null==(s=window.visualViewport)?void 0:s.height)?c:innerHeight,{scrollX:C,scrollY:x}=window,{height:y,width:M,top:H,right:S,bottom:W,left:k}=t.getBoundingClientRect(),{top:Y,right:D,bottom:$,left:I}=(t=>{const e=window.getComputedStyle(t);return{top:parseFloat(e.scrollMarginTop)||0,right:parseFloat(e.scrollMarginRight)||0,bottom:parseFloat(e.scrollMarginBottom)||0,left:parseFloat(e.scrollMarginLeft)||0}})(t);let z="start"===h||"nearest"===h?H-Y:"end"===h?W+$:H+y/2-Y+$,E="center"===p?k+M/2-I+D:"end"===p?S+D:k-I;const N=[];for(let t=0;t<v.length;t++){const e=v[t],{height:n,width:o,top:i,right:a,bottom:s,left:c}=e.getBoundingClientRect();if("if-needed"===d&&H>=0&&k>=0&&W<=F&&S<=w&&(e===g&&!r(e)||H>=i&&W<=s&&k>=c&&S<=a))return N;const u=getComputedStyle(e),f=parseInt(u.borderLeftWidth,10),m=parseInt(u.borderTopWidth,10),b=parseInt(u.borderRightWidth,10),Y=parseInt(u.borderBottomWidth,10);let D=0,$=0;const I="offsetWidth"in e?e.offsetWidth-e.clientWidth-f-b:0,T="offsetHeight"in e?e.offsetHeight-e.clientHeight-m-Y:0,O="offsetWidth"in e?0===e.offsetWidth?0:o/e.offsetWidth:0,A="offsetHeight"in e?0===e.offsetHeight?0:n/e.offsetHeight:0;if(g===e)D="start"===h?z:"end"===h?z-F:"nearest"===h?l(x,x+F,F,m,Y,x+z,x+z+y,y):z-F/2,$="start"===p?E:"center"===p?E-w/2:"end"===p?E-w:l(C,C+w,w,f,b,C+E,C+E+M,M),D=Math.max(0,D+x),$=Math.max(0,$+C);else{D="start"===h?z-i-m:"end"===h?z-s+Y+T:"nearest"===h?l(i,s,n,m,Y+T,z,z+y,y):z-(i+n/2)+T/2,$="start"===p?E-c-f:"center"===p?E-(c+o/2)+I/2:"end"===p?E-a+b+I:l(c,a,o,f,b+I,E,E+M,M);const{scrollLeft:t,scrollTop:r}=e;D=0===A?0:Math.max(0,Math.min(r+D/A,e.scrollHeight-n/A+T)),$=0===O?0:Math.max(0,Math.min(t+$/O,e.scrollWidth-o/O+I)),z+=r-D,E+=t-$}N.push({el:e,top:D,left:$})}return N},c=t=>!1===t?{block:"end",inline:"nearest"}:(t=>t===Object(t)&&0!==Object.keys(t).length)(t)?t:{block:"start",inline:"nearest"};function d(t,e){if(!t.isConnected||!(t=>{let e=t;for(;e&&e.parentNode;){if(e.parentNode===document)return!0;e=e.parentNode instanceof ShadowRoot?e.parentNode.host:e.parentNode}return!1})(t))return;const n=(t=>{const e=window.getComputedStyle(t);return{top:parseFloat(e.scrollMarginTop)||0,right:parseFloat(e.scrollMarginRight)||0,bottom:parseFloat(e.scrollMarginBottom)||0,left:parseFloat(e.scrollMarginLeft)||0}})(t);if((t=>"object"==typeof t&&"function"==typeof t.behavior)(e))return e.behavior(s(t,e));const o="boolean"==typeof e||null==e?void 0:e.behavior;for(const{el:i,top:r,left:l}of s(t,c(e))){const t=r-n.top+n.bottom,e=l-n.left+n.right;i.scroll({top:t,left:e,behavior:o})}}},50317:(t,e,n)=>{n.d(e,{A:()=>p});var o=n(2445),i=n(17437),r=n(72234),l=n(95579),a=n(97470),s=n(18062),c=n(62799),d=n(38380);const h=i.AH`
  &.anticon {
    font-size: unset;
    .anticon {
      line-height: unset;
      vertical-align: unset;
    }
  }
`,p=({name:t,label:e,description:n,validationErrors:p=[],renderTrigger:u=!1,rightNode:f,leftNode:m,onClick:g,hovered:v=!1,tooltipOnClick:b=()=>{},warning:w,danger:F})=>{const C=(0,r.DP)();return e?(0,o.FD)("div",{className:"ControlHeader",children:[(0,o.Y)("div",{className:"pull-left",children:(0,o.FD)(c.l,{css:t=>i.AH`
            margin-bottom: ${.5*t.sizeUnit}px;
            position: relative;
            font-size: ${t.fontSizeSM}px;
          `,htmlFor:t,children:[m&&(0,o.FD)("span",{children:[m," "]}),(0,o.Y)("span",{role:"button",tabIndex:0,onClick:g,style:{cursor:g?"pointer":""},children:e})," ",w&&(0,o.FD)("span",{children:[(0,o.Y)(a.m,{id:"error-tooltip",placement:"top",title:w,children:(0,o.Y)(d.F.WarningOutlined,{iconColor:C.colorWarning,css:i.AH`
                    vertical-align: baseline;
                  `,iconSize:"s"})})," "]}),F&&(0,o.FD)("span",{children:[(0,o.Y)(a.m,{id:"error-tooltip",placement:"top",title:F,children:(0,o.Y)(d.F.CloseCircleOutlined,{iconColor:C.colorErrorText,iconSize:"s"})})," "]}),(null==p?void 0:p.length)>0&&(0,o.FD)("span",{children:[(0,o.Y)(a.m,{id:"error-tooltip",placement:"top",title:null==p?void 0:p.join(" "),children:(0,o.Y)(d.F.CloseCircleOutlined,{iconColor:C.colorErrorText})})," "]}),v?(0,o.FD)("span",{css:()=>i.AH`
          position: absolute;
          top: 60%;
          right: 0;
          padding-left: ${C.sizeUnit}px;
          transform: translate(100%, -50%);
          white-space: nowrap;
        `,children:[n&&(0,o.FD)("span",{children:[(0,o.Y)(a.m,{id:"description-tooltip",title:n,placement:"top",children:(0,o.Y)(d.F.InfoCircleOutlined,{css:h,onClick:b})})," "]}),u&&(0,o.FD)("span",{children:[(0,o.Y)(s.I,{label:(0,l.t)("bolt"),tooltip:(0,l.t)("Changing this control takes effect instantly"),placement:"top",type:"notice"})," "]})]}):null]})}),f&&(0,o.Y)("div",{className:"pull-right",children:f}),(0,o.Y)("div",{className:"clearfix"})]}):null}},56268:(t,e,n)=>{n.d(e,{e:()=>i});var o=n(89467);const i=(0,n(72234).I4)(o.A.Item)`
  ${({theme:t})=>`\n    &.ant-form-item > .ant-row > .ant-form-item-label {\n      padding-bottom: ${t.paddingXXS}px;\n    }\n    .ant-form-item-label {\n      & > label {\n        font-size: ${t.fontSizeSM}px;\n        &.ant-form-item-required:not(.ant-form-item-required-mark-optional) {\n          &::before {\n            display: none;\n          }\n          &::after {\n            display: inline-block;\n            visibility: visible;\n            color: ${t.colorError};\n            font-size: ${t.fontSizeSM}px;\n            content: '*';\n          }\n        }\n      }\n    }\n    .ant-form-item-extra {\n      margin-top: ${t.sizeUnit}px;\n      font-size: ${t.fontSizeSM}px;\n    }\n  `}
`},67874:(t,e,n)=>{n.d(e,{Mo:()=>a,YH:()=>r,j3:()=>l});var o=n(72234),i=n(56268);const r=0,l=o.I4.div`
  min-height: ${({height:t})=>t}px;
  width: ${({width:t})=>t===r?"100%":`${t}px`};
`,a=((0,o.I4)(i.e)`
  &.ant-row.ant-form-item {
    margin: 0;
  }
`,o.I4.div`
  color: ${({theme:t,status:e="error"})=>{var n;return"help"===e?t.colors.grayscale.light1:null==(n=t.colors[e])?void 0:n.base}};
  text-align: ${({centerText:t})=>t?"center":"left"};
  width: 100%;
`)},87615:(t,e,n)=>{n.r(e),n.d(e,{default:()=>p});var o=n(2445),i=n(72234),r=n(72391),l=n(96627),a=n(96540),s=n(39074),c=n(67874);const d=(0,i.I4)(c.j3)`
  display: flex;
  align-items: center;
  overflow-x: auto;

  & .ant-tag {
    margin-right: 0;
  }
`,h=i.I4.div`
  display: flex;
  height: 100%;
  max-width: 100%;
  width: 100%;
  & > div,
  & > div:hover {
    ${({validateStatus:t,theme:e})=>{var n;return t&&`border-color: ${null==(n=e.colors[t])?void 0:n.base}`}}
  }
  & > div {
    width: 100%;
  }
`;function p(t){var e;const{setDataMask:n,setHoveredFilter:i,unsetHoveredFilter:c,setFocusedFilter:p,unsetFocusedFilter:u,setFilterActive:f,width:m,height:g,filterState:v,inputRef:b,isOverflowingFilterBar:w=!1}=t,F=(0,r.a)().get("filter.dateFilterControl"),C=null!=F?F:s.Ay,x=(0,a.useCallback)((t=>{const e=t&&t!==l.WC;n({extraFormData:e?{time_range:t}:{},filterState:{value:e?t:void 0}})}),[n]);return(0,a.useEffect)((()=>{x(v.value)}),[v.value]),null!=(e=t.formData)&&e.inView?(0,o.Y)(d,{width:m,height:g,children:(0,o.Y)(h,{ref:b,validateStatus:v.validateStatus,onFocus:p,onBlur:u,onMouseEnter:i,onMouseLeave:c,children:(0,o.Y)(C,{value:v.value||l.WC,name:t.formData.nativeFilterId||"time_range",onChange:x,onOpenPopover:()=>f(!0),onClosePopover:()=>{f(!1),c(),u()},isOverflowingFilterBar:w})})}):null}}}]);