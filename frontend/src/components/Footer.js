import React from 'react';
import { PhoneIcon, EnvelopeIcon, MapPinIcon } from '@heroicons/react/24/outline';

export default function Footer() {
  return (
    <footer className="w-full bg-gradient-to-t from-gray-50 via-white to-white border-t border-gray-200 shadow-[0_-2px_16px_0_rgba(31,38,135,0.06)] pt-4 pb-2 text-sm">
      <div className="max-w-6xl mx-auto px-4">
        <div className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2 text-center md:text-left">Contact & Info</div>
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          {/* Left: Logo and Brand */}
          <div className="flex items-center mb-2 md:mb-0">
            <img src="/Logo.png" alt="QuantAI Logo" className="h-12 w-auto object-contain" />
            <span className="text-lg font-bold text-gray-900 tracking-tight">QuantAI</span>
          </div>
          {/* Right: Contact Info */}
          <div className="flex flex-col md:flex-row items-center gap-4 md:gap-6 text-gray-500">
            <div className="flex flex-col items-center md:items-start group transition min-w-[120px]">
              <span className="text-[11px] font-semibold text-gray-400 uppercase mb-0.5">Phone</span>
              <div className="flex items-center gap-1">
                <PhoneIcon className="w-4 h-4 text-blue-500 group-hover:text-blue-700 transition-colors" />
                <span className="group-hover:text-gray-900 transition-colors">+64 272115129</span>
              </div>
            </div>
            <span className="hidden md:inline-block text-gray-300">|</span>
            <div className="flex flex-col items-center md:items-start group transition min-w-[120px]">
              <span className="text-[11px] font-semibold text-gray-400 uppercase mb-0.5">Email</span>
              <div className="flex items-center gap-1">
                <EnvelopeIcon className="w-4 h-4 text-blue-500 group-hover:text-blue-700 transition-colors" />
                <a href="mailto:contact@quantai.co.nz" className="hover:underline hover:text-blue-700 transition-colors">contact@quantai.co.nz</a>
              </div>
            </div>
            <span className="hidden md:inline-block text-gray-300">|</span>
            <div className="flex flex-col items-center md:items-start group transition min-w-[120px]">
              <span className="text-[11px] font-semibold text-gray-400 uppercase mb-0.5">Location</span>
              <div className="flex items-center gap-1">
                <MapPinIcon className="w-4 h-4 text-blue-500 group-hover:text-blue-700 transition-colors" />
                <span className="group-hover:text-gray-900 transition-colors">Auckland, NZ</span>
              </div>
            </div>
          </div>
        </div>
        <div className="border-t border-gray-100 mt-3 pt-2 text-center text-xs text-gray-400">&copy; {new Date().getFullYear()} QuantAI. All rights reserved.</div>
      </div>
    </footer>
  );
} 