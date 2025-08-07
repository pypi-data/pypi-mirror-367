"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[6830],{41734:(e,s,t)=>{t.r(s),t.d(s,{UserInfo:()=>x,default:()=>P});var i=t(2445),n=t(96540),a=t(72234),r=t(17437),l=t(35742),o=t(95579),d=t(51713),c=t(5261),u=t(55957),m=t(56268),h=t(17355),p=t(79633);function f({show:e,onHide:s,onSave:t,isEditMode:n,user:a}){const{addDangerToast:r,addSuccessToast:d}=(0,c.Yf)(),u=n?["first_name","last_name"]:["password","confirm_password"],f=n?{first_name:null==a?void 0:a.firstName,last_name:null==a?void 0:a.lastName}:{};return(0,i.Y)(p.k,{show:e,onHide:s,title:n?(0,o.t)("Edit user"):(0,o.t)("Reset password"),onSave:t,formSubmitHandler:async e=>{try{const{confirm_password:s,...i}=e;await l.A.put({endpoint:"/api/v1/me/",jsonPayload:{...i}}),d(n?(0,o.t)("The user was updated successfully"):(0,o.t)("The password reset was successful")),t()}catch(e){r((0,o.t)("Something went wrong while saving the user info"))}},requiredFields:u,initialValues:f,children:n?(0,i.Y)((()=>(0,i.FD)(i.FK,{children:[(0,i.Y)(m.e,{name:"first_name",label:(0,o.t)("First name"),rules:[{required:!0,message:(0,o.t)("First name is required")}],children:(0,i.Y)(h.A,{name:"first_name",placeholder:(0,o.t)("Enter the user's first name")})}),(0,i.Y)(m.e,{name:"last_name",label:(0,o.t)("Last name"),rules:[{required:!0,message:(0,o.t)("Last name is required")}],children:(0,i.Y)(h.A,{name:"last_name",placeholder:(0,o.t)("Enter the user's last name")})})]})),{}):(0,i.Y)((()=>(0,i.FD)(i.FK,{children:[(0,i.Y)(m.e,{name:"password",label:(0,o.t)("Password"),rules:[{required:!0,message:(0,o.t)("Password is required")}],children:(0,i.Y)(h.A.Password,{name:"password",placeholder:"Enter the user's password"})}),(0,i.Y)(m.e,{name:"confirm_password",label:(0,o.t)("Confirm Password"),dependencies:["password"],rules:[{required:!0,message:(0,o.t)("Please confirm your password")},({getFieldValue:e})=>({validator:(s,t)=>t&&e("password")!==t?Promise.reject(new Error((0,o.t)("Passwords do not match!"))):Promise.resolve()})],children:(0,i.Y)(h.A.Password,{name:"confirm_password",placeholder:(0,o.t)("Confirm the user's password")})})]})),{})})}const w=e=>(0,i.Y)(f,{...e,isEditMode:!1}),g=e=>(0,i.Y)(f,{...e,isEditMode:!0});var b=t(38380),Y=t(62683);const y=a.I4.div`
  ${({theme:e})=>r.AH`
    font-weight: ${e.fontWeightStrong};
    text-align: left;
    font-size: 18px;
    padding: ${3*e.sizeUnit}px;
    padding-left: ${7*e.sizeUnit}px;
    display: inline-block;
    line-height: ${9*e.sizeUnit}px;
    width: 100%;
    background-color: ${e.colors.grayscale.light5};
    margin-bottom: ${6*e.sizeUnit}px;
  `}
`,F=a.I4.div`
  ${({theme:e})=>r.AH`
    margin: 0px ${3*e.sizeUnit}px ${6*e.sizeUnit}px
      ${3*e.sizeUnit}px;
    background-color: ${e.colors.grayscale.light5};
  `}
`,S=a.I4.div`
  ${({theme:e})=>r.AH`
    .ant-row {
      margin: 0px ${3*e.sizeUnit}px ${6*e.sizeUnit}px
        ${3*e.sizeUnit}px;
    }
    && .menu > .ant-menu {
      padding: 0px;
    }
    && .nav-right {
      left: 0;
      padding-left: ${4*e.sizeUnit}px;
      position: relative;
      height: ${15*e.sizeUnit}px;
    }
  `}
`,v=a.I4.span`
  font-weight: ${({theme:e})=>e.fontWeightStrong};
`;var A;function x({user:e}){const s=(0,a.DP)(),[t,m]=(0,n.useState)({resetPassword:!1,edit:!1}),h=e=>m((s=>({...s,[e]:!0}))),p=e=>m((s=>({...s,[e]:!1}))),{addDangerToast:f}=(0,c.Yf)(),[x,P]=(0,n.useState)(e);(0,n.useEffect)((()=>{$()}),[]);const $=(0,n.useCallback)((()=>{l.A.get({endpoint:"/api/v1/me/"}).then((({json:e})=>{const s={...e.result,firstName:e.result.first_name,lastName:e.result.last_name};P(s)})).catch((e=>{f("Failed to fetch user info:",e)}))}),[x]),k=[{name:(0,i.FD)(i.FK,{children:[(0,i.Y)(b.F.LockOutlined,{iconColor:s.colorPrimary,iconSize:"m",css:r.AH`
              margin: auto ${2*s.sizeUnit}px auto 0;
              vertical-align: text-top;
            `}),(0,o.t)("Reset my password")]}),buttonStyle:"secondary",onClick:()=>{h(A.ResetPassword)}},{name:(0,i.FD)(i.FK,{children:[(0,i.Y)(b.F.FormOutlined,{iconSize:"m",css:r.AH`
              margin: auto ${2*s.sizeUnit}px auto 0;
              vertical-align: text-top;
            `}),(0,o.t)("Edit user")]}),buttonStyle:"primary",onClick:()=>{h(A.Edit)}}];return(0,i.FD)(S,{children:[(0,i.Y)(y,{children:"Your user information"}),(0,i.Y)(F,{children:(0,i.FD)(Y.S,{defaultActiveKey:["userInfo","personalInfo"],ghost:!0,children:[(0,i.Y)(Y.S.Panel,{header:(0,i.Y)(v,{children:"User info"}),children:(0,i.FD)(u.A,{bordered:!0,size:"small",column:1,labelStyle:{width:"120px"},children:[(0,i.Y)(u.A.Item,{label:"User Name",children:e.username}),(0,i.Y)(u.A.Item,{label:"Is Active?",children:e.isActive?"Yes":"No"}),(0,i.Y)(u.A.Item,{label:"Role",children:e.roles?Object.keys(e.roles).join(", "):"None"}),(0,i.Y)(u.A.Item,{label:"Login count",children:e.loginCount})]})},"userInfo"),(0,i.Y)(Y.S.Panel,{header:(0,i.Y)(v,{children:"Personal info"}),children:(0,i.FD)(u.A,{bordered:!0,size:"small",column:1,labelStyle:{width:"120px"},children:[(0,i.Y)(u.A.Item,{label:"First Name",children:x.firstName}),(0,i.Y)(u.A.Item,{label:"Last Name",children:x.lastName}),(0,i.Y)(u.A.Item,{label:"Email",children:e.email})]})},"personalInfo")]})}),t.resetPassword&&(0,i.Y)(w,{onHide:()=>p(A.ResetPassword),show:t.resetPassword,onSave:()=>{p(A.ResetPassword)}}),t.edit&&(0,i.Y)(g,{onHide:()=>p(A.Edit),show:t.edit,onSave:()=>{p(A.Edit),$()},user:x}),(0,i.Y)(d.A,{buttons:k})]})}!function(e){e.ResetPassword="resetPassword",e.Edit="edit"}(A||(A={}));const P=x},79633:(e,s,t)=>{t.d(s,{k:()=>d});var i=t(2445),n=t(96540),a=t(95579),r=t(15509),l=t(29221),o=t(84335);function d({show:e,onHide:s,title:t,onSave:d,children:c,initialValues:u={},formSubmitHandler:m,bodyStyle:h={},requiredFields:p=[],name:f}){const[w]=l.l.useForm(),[g,b]=(0,n.useState)(!1),Y=(0,n.useCallback)((()=>{w.resetFields(),b(!1)}),[w]),[y,F]=(0,n.useState)(!0),S=(0,n.useCallback)((()=>{Y(),s()}),[s,Y]),v=(0,n.useCallback)((()=>{Y(),d()}),[d,Y]),A=(0,n.useCallback)((async e=>{try{b(!0),await m(e),v()}catch(e){console.error(e)}finally{b(!1)}}),[m,v]),x=()=>{const e=w.getFieldsError().some((({errors:e})=>e.length)),s=w.getFieldsValue(),t=p.some((e=>!s[e]));F(e||t)};return(0,i.Y)(o.aF,{name:f,show:e,title:t,onHide:S,bodyStyle:h,footer:(0,i.FD)(i.FK,{children:[(0,i.Y)(r.$,{buttonStyle:"secondary",onClick:S,children:(0,a.t)("Cancel")}),(0,i.Y)(r.$,{buttonStyle:"primary",htmlType:"submit",onClick:()=>w.submit(),disabled:g||y,children:g?(0,a.t)("Saving..."):(0,a.t)("Save")})]}),children:(0,i.Y)(l.l,{form:w,layout:"vertical",onFinish:A,initialValues:u,onValuesChange:x,onFieldsChange:x,children:"function"==typeof c?c(w):c})})}}}]);