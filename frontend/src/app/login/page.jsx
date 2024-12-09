"use client";
import React from 'react'
import {FaFacebookF, FaGoogle,FaLinkedinIn,FaRegEnvelope } from 'react-icons/fa'
import {MdLockOutline} from 'react-icons/md'

function LoginPage() {
  return (
    <div className='flex flex-col items-center justify-center min-h-screen py-2 bg-blue-100'>
    <main className='flex flex-col items-center justify-center w-full flex-1 px-20 text-center'>
        <div className='bg-white rounded-2xl shadow-2xl flex w-2/3 max-w-4xl'>
            <div className='w-3/5 p-5'>
            <div className='text-left font-bold'><span className='text-blue-300'>GTN Technologies</span>
                </div>
                <div className='py-10'><h2 className='text-3xl font-bold text-blue-400 mb-2'>Sign in to the Account</h2>
                <div className='border-2 w-10 border-blue-500 inline-block mb-2'></div>
                <div className='flex justify-center my-2'>
                    <a href='#' className='border-2 border-gray-200 rounded-full p-3 mx-1'>
                        <FaFacebookF className='text-blue-500 text-sm' />
                    </a>
                    <a href='#' className='border-2 border-gray-200 rounded-full p-3 mx-1'>
                        <FaGoogle className='text-green-300 text-sm' />
                    </a>
                    <a href='#' className='border-2 border-gray-200 rounded-full p-3 mx-1'>
                        <FaLinkedinIn className='text-blue-500 text-sm' />
                    </a>
                </div>
                <p className='text-gray-500 mt-2'>or use your email account:</p>
                <div className='flex flex-col items-center mb-3'>
                    <div className='bg-gray-100 w-64 p-2 flex items-center'><FaRegEnvelope className='text-gray-400 m-2'/>
                    <input type='email' name='email' placeholder='Email' className='bg-gray-100 outline-none text-sm flex-1'></input>
                    </div>
                </div>
                <div className='flex flex-col items-center mb-3'>
                    <div className='bg-gray-100 w-64 p-2 flex items-center'><MdLockOutline className='text-gray-400 m-2'/>
                    <input type='password' name='password' placeholder='Password' className='bg-gray-100 outline-none text-sm flex-1'></input>
                    </div>
                    <div className='flex w-64 mb-5 mt-2 justify-between'><label className='flex items-center text-xs'> <input type='checkbox' name='remeber'></input>Remember me</label>
                    <a href='#' className='text-xs'>Forgot Password</a></div>
                </div>
                <button 
  className="border-2 border-blue-500 rounded-full px-12 py-2 font-semibold hover:bg-blue-500 hover:text-white"
  onClick={() => console.log('Sign in clicked')}
>
  Sign in
</button>
                </div></div>
            <div className='w-2/5 bg-blue-700 text-white rounded-tr-2xl rounded-br-2xl py-36 px-12' ><h2 className='test-3xl font-bold mb-2'>New Here?</h2>
            <div className='border-2 w-10 border-white inline-block mb-2'></div>
            <p className='mb-10'>Create an account to join us.</p>
            <button 
  className="border-2 border-white rounded-full px-12 py-2 font-semibold hover:bg-white hover:text-black"
  onClick={() => console.log('Signup clicked')}
>
  Signup
</button></div>
        </div>
    </main>
</div>
  )
}

export default LoginPage