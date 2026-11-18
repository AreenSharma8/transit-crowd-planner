import type {MetadataRoute} from 'next';
export const dynamic = 'force-static';
export default function manifest():MetadataRoute.Manifest{const basePath=process.env.NEXT_PUBLIC_BASE_PATH||'';return{name:'Nagar Transit Crowd Planner Demo',short_name:'Nagar',description:'Illustrative bus journey and crowding demo',start_url:`${basePath}/`,scope:`${basePath}/`,display:'standalone',background_color:'#f4f6f2',theme_color:'#f4f6f2',icons:[{src:`${basePath}/icon-192.png`,sizes:'192x192',type:'image/png'},{src:`${basePath}/icon-512.png`,sizes:'512x512',type:'image/png'}]}}
