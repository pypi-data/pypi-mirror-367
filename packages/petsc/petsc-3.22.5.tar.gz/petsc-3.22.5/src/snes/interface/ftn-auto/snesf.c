#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* snes.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscsnes.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesseterrorifnotconverged_ SNESSETERRORIFNOTCONVERGED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesseterrorifnotconverged_ snesseterrorifnotconverged
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgeterrorifnotconverged_ SNESGETERRORIFNOTCONVERGED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgeterrorifnotconverged_ snesgeterrorifnotconverged
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetalwayscomputesfinalresidual_ SNESSETALWAYSCOMPUTESFINALRESIDUAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetalwayscomputesfinalresidual_ snessetalwayscomputesfinalresidual
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetalwayscomputesfinalresidual_ SNESGETALWAYSCOMPUTESFINALRESIDUAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetalwayscomputesfinalresidual_ snesgetalwayscomputesfinalresidual
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetfunctiondomainerror_ SNESSETFUNCTIONDOMAINERROR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetfunctiondomainerror_ snessetfunctiondomainerror
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetjacobiandomainerror_ SNESSETJACOBIANDOMAINERROR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetjacobiandomainerror_ snessetjacobiandomainerror
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetcheckjacobiandomainerror_ SNESSETCHECKJACOBIANDOMAINERROR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetcheckjacobiandomainerror_ snessetcheckjacobiandomainerror
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetcheckjacobiandomainerror_ SNESGETCHECKJACOBIANDOMAINERROR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetcheckjacobiandomainerror_ snesgetcheckjacobiandomainerror
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetfunctiondomainerror_ SNESGETFUNCTIONDOMAINERROR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetfunctiondomainerror_ snesgetfunctiondomainerror
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetjacobiandomainerror_ SNESGETJACOBIANDOMAINERROR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetjacobiandomainerror_ snesgetjacobiandomainerror
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesload_ SNESLOAD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesload_ snesload
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesviewfromoptions_ SNESVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesviewfromoptions_ snesviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesview_ SNESVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesview_ snesview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetupmatrices_ SNESSETUPMATRICES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetupmatrices_ snessetupmatrices
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetfromoptions_ SNESSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetfromoptions_ snessetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesresetfromoptions_ SNESRESETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesresetfromoptions_ snesresetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetapplicationcontext_ SNESSETAPPLICATIONCONTEXT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetapplicationcontext_ snessetapplicationcontext
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetapplicationcontext_ SNESGETAPPLICATIONCONTEXT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetapplicationcontext_ snesgetapplicationcontext
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetusematrixfree_ SNESSETUSEMATRIXFREE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetusematrixfree_ snessetusematrixfree
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetusematrixfree_ SNESGETUSEMATRIXFREE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetusematrixfree_ snesgetusematrixfree
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetiterationnumber_ SNESGETITERATIONNUMBER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetiterationnumber_ snesgetiterationnumber
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetiterationnumber_ SNESSETITERATIONNUMBER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetiterationnumber_ snessetiterationnumber
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetnonlinearstepfailures_ SNESGETNONLINEARSTEPFAILURES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetnonlinearstepfailures_ snesgetnonlinearstepfailures
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetmaxnonlinearstepfailures_ SNESSETMAXNONLINEARSTEPFAILURES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetmaxnonlinearstepfailures_ snessetmaxnonlinearstepfailures
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetmaxnonlinearstepfailures_ SNESGETMAXNONLINEARSTEPFAILURES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetmaxnonlinearstepfailures_ snesgetmaxnonlinearstepfailures
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetnumberfunctionevals_ SNESGETNUMBERFUNCTIONEVALS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetnumberfunctionevals_ snesgetnumberfunctionevals
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetlinearsolvefailures_ SNESGETLINEARSOLVEFAILURES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetlinearsolvefailures_ snesgetlinearsolvefailures
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetmaxlinearsolvefailures_ SNESSETMAXLINEARSOLVEFAILURES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetmaxlinearsolvefailures_ snessetmaxlinearsolvefailures
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetmaxlinearsolvefailures_ SNESGETMAXLINEARSOLVEFAILURES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetmaxlinearsolvefailures_ snesgetmaxlinearsolvefailures
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetlinearsolveiterations_ SNESGETLINEARSOLVEITERATIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetlinearsolveiterations_ snesgetlinearsolveiterations
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetcountersreset_ SNESSETCOUNTERSRESET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetcountersreset_ snessetcountersreset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesresetcounters_ SNESRESETCOUNTERS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesresetcounters_ snesresetcounters
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetksp_ SNESSETKSP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetksp_ snessetksp
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesparametersinitialize_ SNESPARAMETERSINITIALIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesparametersinitialize_ snesparametersinitialize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snescreate_ SNESCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snescreate_ snescreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetnormschedule_ SNESSETNORMSCHEDULE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetnormschedule_ snessetnormschedule
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetnormschedule_ SNESGETNORMSCHEDULE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetnormschedule_ snesgetnormschedule
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetfunctionnorm_ SNESSETFUNCTIONNORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetfunctionnorm_ snessetfunctionnorm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetfunctionnorm_ SNESGETFUNCTIONNORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetfunctionnorm_ snesgetfunctionnorm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetupdatenorm_ SNESGETUPDATENORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetupdatenorm_ snesgetupdatenorm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetsolutionnorm_ SNESGETSOLUTIONNORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetsolutionnorm_ snesgetsolutionnorm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetfunctiontype_ SNESSETFUNCTIONTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetfunctiontype_ snessetfunctiontype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetfunctiontype_ SNESGETFUNCTIONTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetfunctiontype_ snesgetfunctiontype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snescomputefunction_ SNESCOMPUTEFUNCTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snescomputefunction_ snescomputefunction
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snescomputemffunction_ SNESCOMPUTEMFFUNCTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snescomputemffunction_ snescomputemffunction
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snescomputengs_ SNESCOMPUTENGS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snescomputengs_ snescomputengs
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snescomputejacobian_ SNESCOMPUTEJACOBIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snescomputejacobian_ snescomputejacobian
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetup_ SNESSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetup_ snessetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesreset_ SNESRESET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesreset_ snesreset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesconvergedreasonviewcancel_ SNESCONVERGEDREASONVIEWCANCEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesconvergedreasonviewcancel_ snesconvergedreasonviewcancel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesdestroy_ SNESDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesdestroy_ snesdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetlagpreconditioner_ SNESSETLAGPRECONDITIONER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetlagpreconditioner_ snessetlagpreconditioner
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetgridsequence_ SNESSETGRIDSEQUENCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetgridsequence_ snessetgridsequence
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetgridsequence_ SNESGETGRIDSEQUENCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetgridsequence_ snesgetgridsequence
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetlagpreconditioner_ SNESGETLAGPRECONDITIONER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetlagpreconditioner_ snesgetlagpreconditioner
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetlagjacobian_ SNESSETLAGJACOBIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetlagjacobian_ snessetlagjacobian
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetlagjacobian_ SNESGETLAGJACOBIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetlagjacobian_ snesgetlagjacobian
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetlagjacobianpersists_ SNESSETLAGJACOBIANPERSISTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetlagjacobianpersists_ snessetlagjacobianpersists
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetlagpreconditionerpersists_ SNESSETLAGPRECONDITIONERPERSISTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetlagpreconditionerpersists_ snessetlagpreconditionerpersists
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetforceiteration_ SNESSETFORCEITERATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetforceiteration_ snessetforceiteration
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetforceiteration_ SNESGETFORCEITERATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetforceiteration_ snesgetforceiteration
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessettolerances_ SNESSETTOLERANCES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessettolerances_ snessettolerances
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetdivergencetolerance_ SNESSETDIVERGENCETOLERANCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetdivergencetolerance_ snessetdivergencetolerance
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgettolerances_ SNESGETTOLERANCES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgettolerances_ snesgettolerances
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetdivergencetolerance_ SNESGETDIVERGENCETOLERANCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetdivergencetolerance_ snesgetdivergencetolerance
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesconverged_ SNESCONVERGED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesconverged_ snesconverged
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesmonitor_ SNESMONITOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesmonitor_ snesmonitor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesmonitorcancel_ SNESMONITORCANCEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesmonitorcancel_ snesmonitorcancel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetconvergedreason_ SNESGETCONVERGEDREASON
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetconvergedreason_ snesgetconvergedreason
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetconvergedreason_ SNESSETCONVERGEDREASON
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetconvergedreason_ snessetconvergedreason
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetconvergencehistory_ SNESSETCONVERGENCEHISTORY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetconvergencehistory_ snessetconvergencehistory
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesconvergedreasonview_ SNESCONVERGEDREASONVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesconvergedreasonview_ snesconvergedreasonview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesconvergedreasonviewfromoptions_ SNESCONVERGEDREASONVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesconvergedreasonviewfromoptions_ snesconvergedreasonviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessolve_ SNESSOLVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessolve_ snessolve
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessettype_ SNESSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessettype_ snessettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgettype_ SNESGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgettype_ snesgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetsolution_ SNESSETSOLUTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetsolution_ snessetsolution
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetsolution_ SNESGETSOLUTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetsolution_ snesgetsolution
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetsolutionupdate_ SNESGETSOLUTIONUPDATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetsolutionupdate_ snesgetsolutionupdate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetoptionsprefix_ SNESSETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetoptionsprefix_ snessetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesappendoptionsprefix_ SNESAPPENDOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesappendoptionsprefix_ snesappendoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetoptionsprefix_ SNESGETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetoptionsprefix_ snesgetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneskspsetuseew_ SNESKSPSETUSEEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneskspsetuseew_ sneskspsetuseew
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneskspgetuseew_ SNESKSPGETUSEEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneskspgetuseew_ sneskspgetuseew
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneskspsetparametersew_ SNESKSPSETPARAMETERSEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneskspsetparametersew_ sneskspsetparametersew
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneskspgetparametersew_ SNESKSPGETPARAMETERSEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneskspgetparametersew_ sneskspgetparametersew
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetksp_ SNESGETKSP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetksp_ snesgetksp
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetdm_ SNESSETDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetdm_ snessetdm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetdm_ SNESGETDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetdm_ snesgetdm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetnpc_ SNESSETNPC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetnpc_ snessetnpc
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetnpc_ SNESGETNPC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetnpc_ snesgetnpc
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneshasnpc_ SNESHASNPC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneshasnpc_ sneshasnpc
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetnpcside_ SNESSETNPCSIDE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetnpcside_ snessetnpcside
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetnpcside_ SNESGETNPCSIDE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetnpcside_ snesgetnpcside
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessetlinesearch_ SNESSETLINESEARCH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessetlinesearch_ snessetlinesearch
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesgetlinesearch_ SNESGETLINESEARCH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesgetlinesearch_ snesgetlinesearch
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  snesseterrorifnotconverged_(SNES snes,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetErrorIfNotConverged(
	(SNES)PetscToPointer((snes) ),*flg);
}
PETSC_EXTERN void  snesgeterrorifnotconverged_(SNES snes,PetscBool *flag, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESGetErrorIfNotConverged(
	(SNES)PetscToPointer((snes) ),flag);
}
PETSC_EXTERN void  snessetalwayscomputesfinalresidual_(SNES snes,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetAlwaysComputesFinalResidual(
	(SNES)PetscToPointer((snes) ),*flg);
}
PETSC_EXTERN void  snesgetalwayscomputesfinalresidual_(SNES snes,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESGetAlwaysComputesFinalResidual(
	(SNES)PetscToPointer((snes) ),flg);
}
PETSC_EXTERN void  snessetfunctiondomainerror_(SNES snes, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetFunctionDomainError(
	(SNES)PetscToPointer((snes) ));
}
PETSC_EXTERN void  snessetjacobiandomainerror_(SNES snes, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetJacobianDomainError(
	(SNES)PetscToPointer((snes) ));
}
PETSC_EXTERN void  snessetcheckjacobiandomainerror_(SNES snes,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetCheckJacobianDomainError(
	(SNES)PetscToPointer((snes) ),*flg);
}
PETSC_EXTERN void  snesgetcheckjacobiandomainerror_(SNES snes,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESGetCheckJacobianDomainError(
	(SNES)PetscToPointer((snes) ),flg);
}
PETSC_EXTERN void  snesgetfunctiondomainerror_(SNES snes,PetscBool *domainerror, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESGetFunctionDomainError(
	(SNES)PetscToPointer((snes) ),domainerror);
}
PETSC_EXTERN void  snesgetjacobiandomainerror_(SNES snes,PetscBool *domainerror, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESGetJacobianDomainError(
	(SNES)PetscToPointer((snes) ),domainerror);
}
PETSC_EXTERN void  snesload_(SNES snes,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(viewer);
*ierr = SNESLoad(
	(SNES)PetscToPointer((snes) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  snesviewfromoptions_(SNES A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = SNESViewFromOptions(
	(SNES)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  snesview_(SNES snes,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(viewer);
*ierr = SNESView(
	(SNES)PetscToPointer((snes) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  snessetupmatrices_(SNES snes, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetUpMatrices(
	(SNES)PetscToPointer((snes) ));
}
PETSC_EXTERN void  snessetfromoptions_(SNES snes, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetFromOptions(
	(SNES)PetscToPointer((snes) ));
}
PETSC_EXTERN void  snesresetfromoptions_(SNES snes, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESResetFromOptions(
	(SNES)PetscToPointer((snes) ));
}
PETSC_EXTERN void  snessetapplicationcontext_(SNES snes,void*usrP, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetApplicationContext(
	(SNES)PetscToPointer((snes) ),usrP);
}
PETSC_EXTERN void  snesgetapplicationcontext_(SNES snes,void*usrP, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESGetApplicationContext(
	(SNES)PetscToPointer((snes) ),usrP);
}
PETSC_EXTERN void  snessetusematrixfree_(SNES snes,PetscBool *mf_operator,PetscBool *mf, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetUseMatrixFree(
	(SNES)PetscToPointer((snes) ),*mf_operator,*mf);
}
PETSC_EXTERN void  snesgetusematrixfree_(SNES snes,PetscBool *mf_operator,PetscBool *mf, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESGetUseMatrixFree(
	(SNES)PetscToPointer((snes) ),mf_operator,mf);
}
PETSC_EXTERN void  snesgetiterationnumber_(SNES snes,PetscInt *iter, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLINTEGER(iter);
*ierr = SNESGetIterationNumber(
	(SNES)PetscToPointer((snes) ),iter);
}
PETSC_EXTERN void  snessetiterationnumber_(SNES snes,PetscInt *iter, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetIterationNumber(
	(SNES)PetscToPointer((snes) ),*iter);
}
PETSC_EXTERN void  snesgetnonlinearstepfailures_(SNES snes,PetscInt *nfails, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLINTEGER(nfails);
*ierr = SNESGetNonlinearStepFailures(
	(SNES)PetscToPointer((snes) ),nfails);
}
PETSC_EXTERN void  snessetmaxnonlinearstepfailures_(SNES snes,PetscInt *maxFails, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetMaxNonlinearStepFailures(
	(SNES)PetscToPointer((snes) ),*maxFails);
}
PETSC_EXTERN void  snesgetmaxnonlinearstepfailures_(SNES snes,PetscInt *maxFails, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLINTEGER(maxFails);
*ierr = SNESGetMaxNonlinearStepFailures(
	(SNES)PetscToPointer((snes) ),maxFails);
}
PETSC_EXTERN void  snesgetnumberfunctionevals_(SNES snes,PetscInt *nfuncs, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLINTEGER(nfuncs);
*ierr = SNESGetNumberFunctionEvals(
	(SNES)PetscToPointer((snes) ),nfuncs);
}
PETSC_EXTERN void  snesgetlinearsolvefailures_(SNES snes,PetscInt *nfails, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLINTEGER(nfails);
*ierr = SNESGetLinearSolveFailures(
	(SNES)PetscToPointer((snes) ),nfails);
}
PETSC_EXTERN void  snessetmaxlinearsolvefailures_(SNES snes,PetscInt *maxFails, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetMaxLinearSolveFailures(
	(SNES)PetscToPointer((snes) ),*maxFails);
}
PETSC_EXTERN void  snesgetmaxlinearsolvefailures_(SNES snes,PetscInt *maxFails, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLINTEGER(maxFails);
*ierr = SNESGetMaxLinearSolveFailures(
	(SNES)PetscToPointer((snes) ),maxFails);
}
PETSC_EXTERN void  snesgetlinearsolveiterations_(SNES snes,PetscInt *lits, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLINTEGER(lits);
*ierr = SNESGetLinearSolveIterations(
	(SNES)PetscToPointer((snes) ),lits);
}
PETSC_EXTERN void  snessetcountersreset_(SNES snes,PetscBool *reset, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetCountersReset(
	(SNES)PetscToPointer((snes) ),*reset);
}
PETSC_EXTERN void  snesresetcounters_(SNES snes, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESResetCounters(
	(SNES)PetscToPointer((snes) ));
}
PETSC_EXTERN void  snessetksp_(SNES snes,KSP ksp, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(ksp);
*ierr = SNESSetKSP(
	(SNES)PetscToPointer((snes) ),
	(KSP)PetscToPointer((ksp) ));
}
PETSC_EXTERN void  snesparametersinitialize_(SNES snes, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESParametersInitialize(
	(SNES)PetscToPointer((snes) ));
}
PETSC_EXTERN void  snescreate_(MPI_Fint * comm,SNES *outsnes, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(outsnes);
 PetscBool outsnes_null = !*(void**) outsnes ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(outsnes);
*ierr = SNESCreate(
	MPI_Comm_f2c(*(comm)),outsnes);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! outsnes_null && !*(void**) outsnes) * (void **) outsnes = (void *)-2;
}
PETSC_EXTERN void  snessetnormschedule_(SNES snes,SNESNormSchedule *normschedule, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetNormSchedule(
	(SNES)PetscToPointer((snes) ),*normschedule);
}
PETSC_EXTERN void  snesgetnormschedule_(SNES snes,SNESNormSchedule *normschedule, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESGetNormSchedule(
	(SNES)PetscToPointer((snes) ),normschedule);
}
PETSC_EXTERN void  snessetfunctionnorm_(SNES snes,PetscReal *norm, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetFunctionNorm(
	(SNES)PetscToPointer((snes) ),*norm);
}
PETSC_EXTERN void  snesgetfunctionnorm_(SNES snes,PetscReal *norm, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLREAL(norm);
*ierr = SNESGetFunctionNorm(
	(SNES)PetscToPointer((snes) ),norm);
}
PETSC_EXTERN void  snesgetupdatenorm_(SNES snes,PetscReal *ynorm, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLREAL(ynorm);
*ierr = SNESGetUpdateNorm(
	(SNES)PetscToPointer((snes) ),ynorm);
}
PETSC_EXTERN void  snesgetsolutionnorm_(SNES snes,PetscReal *xnorm, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLREAL(xnorm);
*ierr = SNESGetSolutionNorm(
	(SNES)PetscToPointer((snes) ),xnorm);
}
PETSC_EXTERN void  snessetfunctiontype_(SNES snes,SNESFunctionType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetFunctionType(
	(SNES)PetscToPointer((snes) ),*type);
}
PETSC_EXTERN void  snesgetfunctiontype_(SNES snes,SNESFunctionType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESGetFunctionType(
	(SNES)PetscToPointer((snes) ),type);
}
PETSC_EXTERN void  snescomputefunction_(SNES snes,Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = SNESComputeFunction(
	(SNES)PetscToPointer((snes) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
PETSC_EXTERN void  snescomputemffunction_(SNES snes,Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = SNESComputeMFFunction(
	(SNES)PetscToPointer((snes) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
PETSC_EXTERN void  snescomputengs_(SNES snes,Vec b,Vec x, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(b);
CHKFORTRANNULLOBJECT(x);
*ierr = SNESComputeNGS(
	(SNES)PetscToPointer((snes) ),
	(Vec)PetscToPointer((b) ),
	(Vec)PetscToPointer((x) ));
}
PETSC_EXTERN void  snescomputejacobian_(SNES snes,Vec X,Mat A,Mat B, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(B);
*ierr = SNESComputeJacobian(
	(SNES)PetscToPointer((snes) ),
	(Vec)PetscToPointer((X) ),
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((B) ));
}
PETSC_EXTERN void  snessetup_(SNES snes, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetUp(
	(SNES)PetscToPointer((snes) ));
}
PETSC_EXTERN void  snesreset_(SNES snes, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESReset(
	(SNES)PetscToPointer((snes) ));
}
PETSC_EXTERN void  snesconvergedreasonviewcancel_(SNES snes, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESConvergedReasonViewCancel(
	(SNES)PetscToPointer((snes) ));
}
PETSC_EXTERN void  snesdestroy_(SNES *snes, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(snes);
 PetscBool snes_null = !*(void**) snes ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESDestroy(snes);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! snes_null && !*(void**) snes) * (void **) snes = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(snes);
 }
PETSC_EXTERN void  snessetlagpreconditioner_(SNES snes,PetscInt *lag, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetLagPreconditioner(
	(SNES)PetscToPointer((snes) ),*lag);
}
PETSC_EXTERN void  snessetgridsequence_(SNES snes,PetscInt *steps, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetGridSequence(
	(SNES)PetscToPointer((snes) ),*steps);
}
PETSC_EXTERN void  snesgetgridsequence_(SNES snes,PetscInt *steps, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLINTEGER(steps);
*ierr = SNESGetGridSequence(
	(SNES)PetscToPointer((snes) ),steps);
}
PETSC_EXTERN void  snesgetlagpreconditioner_(SNES snes,PetscInt *lag, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLINTEGER(lag);
*ierr = SNESGetLagPreconditioner(
	(SNES)PetscToPointer((snes) ),lag);
}
PETSC_EXTERN void  snessetlagjacobian_(SNES snes,PetscInt *lag, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetLagJacobian(
	(SNES)PetscToPointer((snes) ),*lag);
}
PETSC_EXTERN void  snesgetlagjacobian_(SNES snes,PetscInt *lag, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLINTEGER(lag);
*ierr = SNESGetLagJacobian(
	(SNES)PetscToPointer((snes) ),lag);
}
PETSC_EXTERN void  snessetlagjacobianpersists_(SNES snes,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetLagJacobianPersists(
	(SNES)PetscToPointer((snes) ),*flg);
}
PETSC_EXTERN void  snessetlagpreconditionerpersists_(SNES snes,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetLagPreconditionerPersists(
	(SNES)PetscToPointer((snes) ),*flg);
}
PETSC_EXTERN void  snessetforceiteration_(SNES snes,PetscBool *force, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetForceIteration(
	(SNES)PetscToPointer((snes) ),*force);
}
PETSC_EXTERN void  snesgetforceiteration_(SNES snes,PetscBool *force, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESGetForceIteration(
	(SNES)PetscToPointer((snes) ),force);
}
PETSC_EXTERN void  snessettolerances_(SNES snes,PetscReal *abstol,PetscReal *rtol,PetscReal *stol,PetscInt *maxit,PetscInt *maxf, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetTolerances(
	(SNES)PetscToPointer((snes) ),*abstol,*rtol,*stol,*maxit,*maxf);
}
PETSC_EXTERN void  snessetdivergencetolerance_(SNES snes,PetscReal *divtol, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetDivergenceTolerance(
	(SNES)PetscToPointer((snes) ),*divtol);
}
PETSC_EXTERN void  snesgettolerances_(SNES snes,PetscReal *atol,PetscReal *rtol,PetscReal *stol,PetscInt *maxit,PetscInt *maxf, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLREAL(atol);
CHKFORTRANNULLREAL(rtol);
CHKFORTRANNULLREAL(stol);
CHKFORTRANNULLINTEGER(maxit);
CHKFORTRANNULLINTEGER(maxf);
*ierr = SNESGetTolerances(
	(SNES)PetscToPointer((snes) ),atol,rtol,stol,maxit,maxf);
}
PETSC_EXTERN void  snesgetdivergencetolerance_(SNES snes,PetscReal *divtol, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLREAL(divtol);
*ierr = SNESGetDivergenceTolerance(
	(SNES)PetscToPointer((snes) ),divtol);
}
PETSC_EXTERN void  snesconverged_(SNES snes,PetscInt *it,PetscReal *xnorm,PetscReal *snorm,PetscReal *fnorm, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESConverged(
	(SNES)PetscToPointer((snes) ),*it,*xnorm,*snorm,*fnorm);
}
PETSC_EXTERN void  snesmonitor_(SNES snes,PetscInt *iter,PetscReal *rnorm, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESMonitor(
	(SNES)PetscToPointer((snes) ),*iter,*rnorm);
}
PETSC_EXTERN void  snesmonitorcancel_(SNES snes, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESMonitorCancel(
	(SNES)PetscToPointer((snes) ));
}
PETSC_EXTERN void  snesgetconvergedreason_(SNES snes,SNESConvergedReason *reason, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESGetConvergedReason(
	(SNES)PetscToPointer((snes) ),reason);
}
PETSC_EXTERN void  snessetconvergedreason_(SNES snes,SNESConvergedReason *reason, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetConvergedReason(
	(SNES)PetscToPointer((snes) ),*reason);
}
PETSC_EXTERN void  snessetconvergencehistory_(SNES snes,PetscReal a[],PetscInt its[],PetscInt *na,PetscBool *reset, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLREAL(a);
CHKFORTRANNULLINTEGER(its);
*ierr = SNESSetConvergenceHistory(
	(SNES)PetscToPointer((snes) ),a,its,*na,*reset);
}
PETSC_EXTERN void  snesconvergedreasonview_(SNES snes,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(viewer);
*ierr = SNESConvergedReasonView(
	(SNES)PetscToPointer((snes) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  snesconvergedreasonviewfromoptions_(SNES snes, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESConvergedReasonViewFromOptions(
	(SNES)PetscToPointer((snes) ));
}
PETSC_EXTERN void  snessolve_(SNES snes,Vec b,Vec x, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(b);
CHKFORTRANNULLOBJECT(x);
*ierr = SNESSolve(
	(SNES)PetscToPointer((snes) ),
	(Vec)PetscToPointer((b) ),
	(Vec)PetscToPointer((x) ));
}
PETSC_EXTERN void  snessettype_(SNES snes,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(snes);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = SNESSetType(
	(SNES)PetscToPointer((snes) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  snesgettype_(SNES snes,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESGetType(
	(SNES)PetscToPointer((snes) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  snessetsolution_(SNES snes,Vec u, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(u);
*ierr = SNESSetSolution(
	(SNES)PetscToPointer((snes) ),
	(Vec)PetscToPointer((u) ));
}
PETSC_EXTERN void  snesgetsolution_(SNES snes,Vec *x, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool x_null = !*(void**) x ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(x);
*ierr = SNESGetSolution(
	(SNES)PetscToPointer((snes) ),x);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! x_null && !*(void**) x) * (void **) x = (void *)-2;
}
PETSC_EXTERN void  snesgetsolutionupdate_(SNES snes,Vec *x, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool x_null = !*(void**) x ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(x);
*ierr = SNESGetSolutionUpdate(
	(SNES)PetscToPointer((snes) ),x);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! x_null && !*(void**) x) * (void **) x = (void *)-2;
}
PETSC_EXTERN void  snessetoptionsprefix_(SNES snes, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(snes);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = SNESSetOptionsPrefix(
	(SNES)PetscToPointer((snes) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  snesappendoptionsprefix_(SNES snes, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(snes);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = SNESAppendOptionsPrefix(
	(SNES)PetscToPointer((snes) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  snesgetoptionsprefix_(SNES snes, char *prefix, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESGetOptionsPrefix(
	(SNES)PetscToPointer((snes) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for prefix */
*ierr = PetscStrncpy(prefix, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, prefix, cl0);
}
PETSC_EXTERN void  sneskspsetuseew_(SNES snes,PetscBool *flag, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESKSPSetUseEW(
	(SNES)PetscToPointer((snes) ),*flag);
}
PETSC_EXTERN void  sneskspgetuseew_(SNES snes,PetscBool *flag, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESKSPGetUseEW(
	(SNES)PetscToPointer((snes) ),flag);
}
PETSC_EXTERN void  sneskspsetparametersew_(SNES snes,PetscInt *version,PetscReal *rtol_0,PetscReal *rtol_max,PetscReal *gamma,PetscReal *alpha,PetscReal *alpha2,PetscReal *threshold, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESKSPSetParametersEW(
	(SNES)PetscToPointer((snes) ),*version,*rtol_0,*rtol_max,*gamma,*alpha,*alpha2,*threshold);
}
PETSC_EXTERN void  sneskspgetparametersew_(SNES snes,PetscInt *version,PetscReal *rtol_0,PetscReal *rtol_max,PetscReal *gamma,PetscReal *alpha,PetscReal *alpha2,PetscReal *threshold, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLINTEGER(version);
CHKFORTRANNULLREAL(rtol_0);
CHKFORTRANNULLREAL(rtol_max);
CHKFORTRANNULLREAL(gamma);
CHKFORTRANNULLREAL(alpha);
CHKFORTRANNULLREAL(alpha2);
CHKFORTRANNULLREAL(threshold);
*ierr = SNESKSPGetParametersEW(
	(SNES)PetscToPointer((snes) ),version,rtol_0,rtol_max,gamma,alpha,alpha2,threshold);
}
PETSC_EXTERN void  snesgetksp_(SNES snes,KSP *ksp, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool ksp_null = !*(void**) ksp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ksp);
*ierr = SNESGetKSP(
	(SNES)PetscToPointer((snes) ),ksp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ksp_null && !*(void**) ksp) * (void **) ksp = (void *)-2;
}
PETSC_EXTERN void  snessetdm_(SNES snes,DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(dm);
*ierr = SNESSetDM(
	(SNES)PetscToPointer((snes) ),
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  snesgetdm_(SNES snes,DM *dm, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = SNESGetDM(
	(SNES)PetscToPointer((snes) ),dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
PETSC_EXTERN void  snessetnpc_(SNES snes,SNES npc, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(npc);
*ierr = SNESSetNPC(
	(SNES)PetscToPointer((snes) ),
	(SNES)PetscToPointer((npc) ));
}
PETSC_EXTERN void  snesgetnpc_(SNES snes,SNES *pc, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool pc_null = !*(void**) pc ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(pc);
*ierr = SNESGetNPC(
	(SNES)PetscToPointer((snes) ),pc);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! pc_null && !*(void**) pc) * (void **) pc = (void *)-2;
}
PETSC_EXTERN void  sneshasnpc_(SNES snes,PetscBool *has_npc, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESHasNPC(
	(SNES)PetscToPointer((snes) ),has_npc);
}
PETSC_EXTERN void  snessetnpcside_(SNES snes,PCSide *side, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetNPCSide(
	(SNES)PetscToPointer((snes) ),*side);
}
PETSC_EXTERN void  snesgetnpcside_(SNES snes,PCSide *side, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESGetNPCSide(
	(SNES)PetscToPointer((snes) ),side);
}
PETSC_EXTERN void  snessetlinesearch_(SNES snes,SNESLineSearch linesearch, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(linesearch);
*ierr = SNESSetLineSearch(
	(SNES)PetscToPointer((snes) ),
	(SNESLineSearch)PetscToPointer((linesearch) ));
}
PETSC_EXTERN void  snesgetlinesearch_(SNES snes,SNESLineSearch *linesearch, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool linesearch_null = !*(void**) linesearch ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(linesearch);
*ierr = SNESGetLineSearch(
	(SNES)PetscToPointer((snes) ),linesearch);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! linesearch_null && !*(void**) linesearch) * (void **) linesearch = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
