import React from 'react';

const CustomNumberInput = ({ id, name, value, onChange, required, className }) => {
    return (
        <input
            type="number"
            id={id}
            name={name}
            value={value}
            onChange={onChange}
            pattern="^\d*\.?\d*$"
            onKeyDown={(e) => {
                if (
                    !/[0-9]/.test(e.key) &&
                    e.key !== 'Backspace' &&
                    e.key !== 'ArrowLeft' &&
                    e.key !== 'ArrowRight' &&
                    e.key !== 'Delete' &&
                    !(e.ctrlKey || e.metaKey) // Allow Ctrl or Cmd combinations
                ) {
                    e.preventDefault();
                }
            }}
            required={required}
            className={`mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-2 no-spin ${className}`}
        />
    );
};

const CustomFloatInput = ({ id, name, value, onChange, required, className }) => {
   
    return (
        <input
            type="text"
            inputMode="decimal"
            id={id}
            name={name}
            value={value}
            onChange={onChange}
            onKeyDown={(e) => {
                if (
                    !/[0-9]/.test(e.key) &&
                    e.key !== 'Backspace' &&
                    e.key !== 'ArrowLeft' &&
                    e.key !== 'ArrowRight' &&
                    e.key !== 'Delete' &&
                    e.key !== "." && !value.includes('.') &&
                    !(e.ctrlKey || e.metaKey) // Allow Ctrl or Cmd combinations
                ) {
                    e.preventDefault();
                }
            }}
            required={required}
            className={`mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-2 no-spin ${className}`}
        />
    );
};

export { CustomNumberInput, CustomFloatInput };
