import React, { useState, useEffect } from 'react';
import { 
  Package, 
  CheckCircle2,
  MapPin,
  X,
  LayoutGrid,
  ArrowLeft,
  PlusCircle,
  History,
  ArrowUpRight,
  ArrowDownLeft,
  User,
  Hash,
  Globe,
  Terminal,
  Search,
  Copy,
  Plus,
  Server,
  Network
} from 'lucide-react';

export default function App() {
  const [currentPage, setCurrentPage] = useState('home'); 
  const [notification, setNotification] = useState(null);

  // --- СОСТОЯНИЕ: СКЛАД ---
  const [inventory, setInventory] = useState([
    { id: '1', name: 'Коммутатор Eltex MES2324', unit: 'шт', quantity: 5, serials: 'ELX-001, ELX-002, ELX-003, ELX-004, ELX-005' },
    { id: '2', name: 'Оптический патч-корд LC-LC 3м', unit: 'шт', quantity: 42, serials: '-' },
  ]);
  
  const [invHistory, setInvHistory] = useState([
    { id: 'h1', date: new Date().toLocaleString(), type: 'in', name: 'Коммутатор Eltex MES2324', amount: 5, user: 'Админ', details: 'Начальное оприходование' }
  ]);
  
  const [inventoryTab, setInventoryTab] = useState('list'); 
  const [showWriteOff, setShowWriteOff] = useState(null); 
  const [writeOffForm, setWriteOffForm] = useState({ amount: '1', serial: '', account: '', address: '', ticket: '' });

  // --- СОСТОЯНИЕ: IP МЕНЕДЖЕР ---
  const [ipList, setIpList] = useState([
    { id: 'ip1', ip: '192.168.10.1', device: 'Gateway-Core', vlan: '10', status: 'active' },
    { id: 'ip2', ip: '192.168.10.25', device: 'Switch-Floor1', vlan: '10', status: 'active' },
    { id: 'ip3', ip: '192.168.20.5', device: 'Reserved', vlan: '20', status: 'reserved' },
  ]);

  // --- СОСТОЯНИЕ: КОНФИГУРАТОР ---
  const [confParams, setConfParams] = useState({ type: 'access', vlan: '100', port: '1/0/1', desc: 'UPLINK' });

  const showNotification = (message) => {
    setNotification(message);
    setTimeout(() => setNotification(null), 3000);
  };

  const copyToClipboard = (text) => {
    const el = document.createElement('textarea');
    el.value = text;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    showNotification('Скопировано в буфер');
  };

  // --- КОМПОНЕНТ: СКЛАД ---
  const InventoryManager = () => {
    const [addFormData, setAddFormData] = useState({ name: '', unit: 'шт', quantity: '', serials: '' });
    const [searchTerm, setSearchTerm] = useState('');

    const filteredInventory = inventory.filter(item => 
      item.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
      item.serials.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const handleAdd = () => {
      if (!addFormData.name || !addFormData.quantity) return;
      const numQty = parseFloat(addFormData.quantity);
      setInventory([...inventory, { ...addFormData, id: Date.now().toString(), quantity: numQty }]);
      setInvHistory([{ id: 'h' + Date.now(), date: new Date().toLocaleString(), type: 'in', name: addFormData.name, amount: numQty, user: 'Админ' }, ...invHistory]);
      setAddFormData({ name: '', unit: 'шт', quantity: '', serials: '' });
      showNotification('Товар добавлен');
    };

    const confirmWriteOff = () => {
      const item = inventory.find(i => i.id === showWriteOff);
      const amount = parseFloat(writeOffForm.amount);
      if (!item || amount > item.quantity) return;

      let updatedSerials = item.serials;
      if (writeOffForm.serial && item.serials !== '-') {
        const serialsArr = item.serials.split(',').map(s => s.trim());
        const index = serialsArr.indexOf(writeOffForm.serial);
        if (index > -1) {
          serialsArr.splice(index, 1);
          updatedSerials = serialsArr.join(', ') || '-';
        }
      }

      setInventory(inventory.map(i => i.id === showWriteOff ? { ...i, quantity: i.quantity - amount, serials: updatedSerials } : i));
      setInvHistory([{ id: 'h' + Date.now(), date: new Date().toLocaleString(), type: 'out', name: item.name, amount, user: 'Админ', details: `Заявка: ${writeOffForm.ticket || '-'}` }, ...invHistory]);
      setShowWriteOff(null);
      showNotification('Списание выполнено');
    };

    return (
      <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-300">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <button onClick={() => setCurrentPage('home')} className="p-2 hover:bg-slate-200 rounded-full"><ArrowLeft size={24}/></button>
            <h2 className="text-2xl font-black">Склад</h2>
          </div>
          <div className="flex p-1 bg-slate-200 rounded-xl">
            <button onClick={() => setInventoryTab('list')} className={`px-4 py-1.5 rounded-lg text-sm font-bold ${inventoryTab === 'list' ? 'bg-white shadow text-indigo-600' : 'text-slate-500'}`}>Наличие</button>
            <button onClick={() => setInventoryTab('history')} className={`px-4 py-1.5 rounded-lg text-sm font-bold ${inventoryTab === 'history' ? 'bg-white shadow text-indigo-600' : 'text-slate-500'}`}>История</button>
          </div>
        </div>

        {inventoryTab === 'list' ? (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-4 bg-white p-6 rounded-[2rem] border shadow-sm">
              <h3 className="font-black mb-4 flex items-center gap-2"><PlusCircle size={18}/> Приход</h3>
              <div className="space-y-3">
                <input type="text" placeholder="Название" className="w-full p-3 border rounded-xl font-bold" value={addFormData.name} onChange={e => setAddFormData({...addFormData, name: e.target.value})} />
                <div className="grid grid-cols-2 gap-2">
                  <input type="number" placeholder="Кол-во" className="w-full p-3 border rounded-xl font-bold" value={addFormData.quantity} onChange={e => setAddFormData({...addFormData, quantity: e.target.value})} />
                  <select className="p-3 border rounded-xl font-bold bg-slate-50" value={addFormData.unit} onChange={e => setAddFormData({...addFormData, unit: e.target.value})}><option>шт</option><option>м</option></select>
                </div>
                <textarea placeholder="Серийники" className="w-full p-3 border rounded-xl h-20 text-xs font-mono" value={addFormData.serials} onChange={e => setAddFormData({...addFormData, serials: e.target.value})} />
                <button onClick={handleAdd} className="w-full py-3 bg-indigo-600 text-white rounded-xl font-black">Добавить</button>
              </div>
            </div>
            <div className="lg:col-span-8 space-y-4">
              <div className="bg-white rounded-[2rem] border overflow-hidden">
                <table className="w-full text-left">
                  <thead className="bg-slate-50 text-[10px] font-black uppercase text-slate-400">
                    <tr><th className="p-4">Товар</th><th className="p-4">Остаток</th><th className="p-4 text-right">Действие</th></tr>
                  </thead>
                  <tbody className="divide-y">
                    {filteredInventory.map(item => (
                      <tr key={item.id} className="hover:bg-slate-50">
                        <td className="p-4"><div className="font-bold">{item.name}</div><div className="text-[10px] text-slate-400 font-mono">SN: {item.serials}</div></td>
                        <td className="p-4 font-black">{item.quantity} {item.unit}</td>
                        <td className="p-4 text-right"><button onClick={() => setShowWriteOff(item.id)} className="px-3 py-1 bg-red-50 text-red-600 rounded-lg text-xs font-bold">Списать</button></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-[2rem] border divide-y shadow-sm">
            {invHistory.map(h => (
              <div key={h.id} className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${h.type === 'in' ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-600'}`}>
                    {h.type === 'in' ? <ArrowDownLeft size={16}/> : <ArrowUpRight size={16}/>}
                  </div>
                  <div><div className="font-bold text-sm">{h.name}</div><div className="text-[10px] text-slate-400 uppercase">{h.date}</div></div>
                </div>
                <div className={`font-black ${h.type === 'in' ? 'text-emerald-600' : 'text-red-600'}`}>{h.type === 'in' ? '+' : '-'}{h.amount}</div>
              </div>
            ))}
          </div>
        )}

        {showWriteOff && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div className="bg-white rounded-[2rem] w-full max-w-md p-6 shadow-2xl relative">
               <button onClick={() => setShowWriteOff(null)} className="absolute top-4 right-4 text-slate-400"><X size={20}/></button>
               <h3 className="text-xl font-black mb-4">Списание ТМЦ</h3>
               <div className="space-y-3">
                 <input type="number" className="w-full p-3 border rounded-xl font-black" value={writeOffForm.amount} onChange={e => setWriteOffForm({...writeOffForm, amount: e.target.value})} placeholder="Кол-во" />
                 <input type="text" placeholder="Адрес объекта" className="w-full p-3 border rounded-xl font-bold" value={writeOffForm.address} onChange={e => setWriteOffForm({...writeOffForm, address: e.target.value})} />
                 <button onClick={confirmWriteOff} className="w-full py-4 bg-red-600 text-white rounded-xl font-black">Подтвердить</button>
               </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  // --- КОМПОНЕНТ: IP МЕНЕДЖЕР ---
  const IPManager = () => {
    const [newIp, setNewIp] = useState({ ip: '', device: '', vlan: '', status: 'active' });

    const addIp = () => {
      if (!newIp.ip) return;
      setIpList([{...newIp, id: Date.now().toString()}, ...ipList]);
      setNewIp({ ip: '', device: '', vlan: '', status: 'active' });
      showNotification('IP добавлен в базу');
    };

    return (
      <div className="space-y-6 animate-in slide-in-from-right-4 duration-300">
        <div className="flex items-center gap-4 mb-4">
          <button onClick={() => setCurrentPage('home')} className="p-2 hover:bg-slate-200 rounded-full"><ArrowLeft size={24}/></button>
          <h2 className="text-2xl font-black">IP Менеджер</h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-4 bg-white p-6 rounded-[2rem] border shadow-sm h-fit">
            <h3 className="font-black mb-4 flex items-center gap-2"><Plus size={18}/> Зарезервировать IP</h3>
            <div className="space-y-3">
              <input type="text" placeholder="IP Адрес" className="w-full p-3 border rounded-xl font-bold" value={newIp.ip} onChange={e => setNewIp({...newIp, ip: e.target.value})} />
              <input type="text" placeholder="Устройство / Назначение" className="w-full p-3 border rounded-xl font-bold" value={newIp.device} onChange={e => setNewIp({...newIp, device: e.target.value})} />
              <input type="text" placeholder="VLAN" className="w-full p-3 border rounded-xl font-bold" value={newIp.vlan} onChange={e => setNewIp({...newIp, vlan: e.target.value})} />
              <button onClick={addIp} className="w-full py-3 bg-indigo-600 text-white rounded-xl font-black">Добавить</button>
            </div>
          </div>

          <div className="lg:col-span-8 bg-white rounded-[2rem] border overflow-hidden shadow-sm">
            <table className="w-full text-left">
              <thead className="bg-slate-50 text-[10px] font-black uppercase text-slate-400">
                <tr><th className="p-4">IP Адрес</th><th className="p-4">Устройство</th><th className="p-4">VLAN</th><th className="p-4">Статус</th></tr>
              </thead>
              <tbody className="divide-y">
                {ipList.map(ip => (
                  <tr key={ip.id} className="hover:bg-slate-50">
                    <td className="p-4 font-mono font-bold text-indigo-600">{ip.ip}</td>
                    <td className="p-4 font-bold">{ip.device || '-'}</td>
                    <td className="p-4"><span className="bg-slate-100 px-2 py-1 rounded text-xs font-bold text-slate-600">vlan {ip.vlan}</span></td>
                    <td className="p-4">
                      <span className={`text-[10px] font-black uppercase px-2 py-1 rounded-full ${ip.status === 'active' ? 'bg-emerald-100 text-emerald-600' : 'bg-amber-100 text-amber-600'}`}>
                        {ip.status === 'active' ? 'Активен' : 'Бронь'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };

  // --- КОМПОНЕНТ: КОНФИГУРАТОР ---
  const Configurator = () => {
    const generateConfig = () => {
      if (confParams.type === 'access') {
        return `interface GigabithEthernet ${confParams.port}\n description ${confParams.desc}\n switchport mode access\n switchport access vlan ${confParams.vlan}\n spanning-tree portfast\n exit`;
      } else {
        return `interface GigabithEthernet ${confParams.port}\n description ${confParams.desc}\n switchport mode trunk\n switchport trunk allowed vlan add ${confParams.vlan}\n exit`;
      }
    };

    return (
      <div className="space-y-6 animate-in slide-in-from-left-4 duration-300">
        <div className="flex items-center gap-4 mb-4">
          <button onClick={() => setCurrentPage('home')} className="p-2 hover:bg-slate-200 rounded-full"><ArrowLeft size={24}/></button>
          <h2 className="text-2xl font-black">Генератор команд</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-[2rem] border shadow-sm space-y-4">
            <h3 className="font-black flex items-center gap-2"><Settings size={18}/> Настройки порта</h3>
            <div>
              <label className="text-[10px] font-black uppercase text-slate-400 block mb-1 ml-1">Тип порта</label>
              <select className="w-full p-3 border rounded-xl font-bold bg-slate-50" value={confParams.type} onChange={e => setConfParams({...confParams, type: e.target.value})}>
                <option value="access">Access (Абонент)</option>
                <option value="trunk">Trunk (Магистраль)</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[10px] font-black uppercase text-slate-400 block mb-1 ml-1">Номер порта</label>
                <input type="text" className="w-full p-3 border rounded-xl font-bold" value={confParams.port} onChange={e => setConfParams({...confParams, port: e.target.value})} />
              </div>
              <div>
                <label className="text-[10px] font-black uppercase text-slate-400 block mb-1 ml-1">VLAN ID</label>
                <input type="text" className="w-full p-3 border rounded-xl font-bold" value={confParams.vlan} onChange={e => setConfParams({...confParams, vlan: e.target.value})} />
              </div>
            </div>
            <div>
              <label className="text-[10px] font-black uppercase text-slate-400 block mb-1 ml-1">Описание (Description)</label>
              <input type="text" className="w-full p-3 border rounded-xl font-bold" value={confParams.desc} onChange={e => setConfParams({...confParams, desc: e.target.value})} />
            </div>
          </div>

          <div className="bg-slate-900 rounded-[2rem] p-6 text-emerald-400 font-mono text-sm relative group overflow-hidden">
            <div className="flex justify-between items-center mb-4 text-slate-500 font-sans border-b border-slate-800 pb-2">
              <span className="text-[10px] font-black uppercase tracking-widest">Output: Cisco/Eltex CLI</span>
              <button onClick={() => copyToClipboard(generateConfig())} className="hover:text-white transition-colors"><Copy size={16}/></button>
            </div>
            <pre className="whitespace-pre-wrap leading-relaxed">
              {generateConfig()}
            </pre>
            <div className="absolute inset-0 bg-emerald-500/5 pointer-events-none opacity-20"></div>
          </div>
        </div>
      </div>
    );
  };

  // --- ГЛАВНАЯ СТРАНИЦА ---
  const HomePage = () => (
    <div className="max-w-4xl mx-auto pt-12 animate-in zoom-in-95 duration-500 px-4">
      <div className="text-center mb-12">
        <h1 className="text-6xl font-black text-slate-900 tracking-tighter mb-4 italic">S-CONTROL</h1>
        <p className="text-slate-400 font-bold text-lg">Единая рабочая среда инженера связи.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button onClick={() => setCurrentPage('inventory')} className="p-8 rounded-[2.5rem] bg-indigo-600 text-white text-left shadow-lg shadow-indigo-100 hover:scale-[1.02] transition-all flex justify-between items-end group">
          <div><Package size={40} className="mb-4"/><h3 className="text-2xl font-black">Склад ТМЦ</h3><p className="text-sm opacity-80">Остатки, серийники, списание.</p></div>
          <ArrowUpRight className="opacity-0 group-hover:opacity-100 transition-all"/>
        </button>

        <button onClick={() => setCurrentPage('ipmanager')} className="p-8 rounded-[2.5rem] bg-emerald-600 text-white text-left shadow-lg shadow-emerald-100 hover:scale-[1.02] transition-all flex justify-between items-end group">
          <div><Globe size={40} className="mb-4"/><h3 className="text-2xl font-black">IP Менеджер</h3><p className="text-sm opacity-80">База адресов, резервы, VLAN.</p></div>
          <ArrowUpRight className="opacity-0 group-hover:opacity-100 transition-all"/>
        </button>

        <button onClick={() => setCurrentPage('configurator')} className="p-8 rounded-[2.5rem] bg-slate-800 text-white text-left shadow-lg shadow-slate-200 hover:scale-[1.02] transition-all flex justify-between items-end group md:col-span-2">
          <div><Terminal size={40} className="mb-4"/><h3 className="text-2xl font-black">Конфигуратор</h3><p className="text-sm opacity-80">Генератор CLI команд для Eltex, Cisco, SNR.</p></div>
          <ArrowUpRight className="opacity-0 group-hover:opacity-100 transition-all"/>
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#F8FAFC] pb-20">
      <nav className="bg-white/80 backdrop-blur-md border-b sticky top-0 z-50 h-16 flex items-center px-6">
        <div className="max-w-5xl mx-auto w-full flex justify-between items-center">
          <button onClick={() => setCurrentPage('home')} className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white"><LayoutGrid size={18}/></div>
            <span className="font-black tracking-tight text-lg">S-CONTROL</span>
          </button>
          <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-xl">
             <div className="w-8 h-8 bg-slate-900 rounded-lg flex items-center justify-center text-white font-black text-[10px]">DA</div>
          </div>
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-4 mt-8">
        {currentPage === 'home' && <HomePage />}
        {currentPage === 'inventory' && <InventoryManager />}
        {currentPage === 'ipmanager' && <IPManager />}
        {currentPage === 'configurator' && <Configurator />}
      </main>

      {notification && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-slate-900 text-white px-6 py-3 rounded-2xl shadow-xl flex items-center gap-3 z-[200] animate-in slide-in-from-bottom-5">
          <CheckCircle2 size={16} className="text-emerald-400" />
          <span className="text-xs font-black uppercase tracking-wider">{notification}</span>
        </div>
      )}
    </div>
  );
}
