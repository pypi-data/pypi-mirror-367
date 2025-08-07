#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* factor.c */
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

#include "petscpc.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorsetupmatsolvertype_ PCFACTORSETUPMATSOLVERTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorsetupmatsolvertype_ pcfactorsetupmatsolvertype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorsetzeropivot_ PCFACTORSETZEROPIVOT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorsetzeropivot_ pcfactorsetzeropivot
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorsetshifttype_ PCFACTORSETSHIFTTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorsetshifttype_ pcfactorsetshifttype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorsetshiftamount_ PCFACTORSETSHIFTAMOUNT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorsetshiftamount_ pcfactorsetshiftamount
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorsetdroptolerance_ PCFACTORSETDROPTOLERANCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorsetdroptolerance_ pcfactorsetdroptolerance
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorgetzeropivot_ PCFACTORGETZEROPIVOT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorgetzeropivot_ pcfactorgetzeropivot
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorgetshiftamount_ PCFACTORGETSHIFTAMOUNT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorgetshiftamount_ pcfactorgetshiftamount
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorgetshifttype_ PCFACTORGETSHIFTTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorgetshifttype_ pcfactorgetshifttype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorgetlevels_ PCFACTORGETLEVELS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorgetlevels_ pcfactorgetlevels
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorsetlevels_ PCFACTORSETLEVELS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorsetlevels_ pcfactorsetlevels
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorsetallowdiagonalfill_ PCFACTORSETALLOWDIAGONALFILL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorsetallowdiagonalfill_ pcfactorsetallowdiagonalfill
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorgetallowdiagonalfill_ PCFACTORGETALLOWDIAGONALFILL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorgetallowdiagonalfill_ pcfactorgetallowdiagonalfill
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorreorderfornonzerodiagonal_ PCFACTORREORDERFORNONZERODIAGONAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorreorderfornonzerodiagonal_ pcfactorreorderfornonzerodiagonal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorsetmatsolvertype_ PCFACTORSETMATSOLVERTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorsetmatsolvertype_ pcfactorsetmatsolvertype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorgetmatsolvertype_ PCFACTORGETMATSOLVERTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorgetmatsolvertype_ pcfactorgetmatsolvertype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorsetfill_ PCFACTORSETFILL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorsetfill_ pcfactorsetfill
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorsetuseinplace_ PCFACTORSETUSEINPLACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorsetuseinplace_ pcfactorsetuseinplace
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorgetuseinplace_ PCFACTORGETUSEINPLACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorgetuseinplace_ pcfactorgetuseinplace
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorsetmatorderingtype_ PCFACTORSETMATORDERINGTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorsetmatorderingtype_ pcfactorsetmatorderingtype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorsetcolumnpivot_ PCFACTORSETCOLUMNPIVOT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorsetcolumnpivot_ pcfactorsetcolumnpivot
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorsetpivotinblocks_ PCFACTORSETPIVOTINBLOCKS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorsetpivotinblocks_ pcfactorsetpivotinblocks
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcfactorsetreusefill_ PCFACTORSETREUSEFILL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcfactorsetreusefill_ pcfactorsetreusefill
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  pcfactorsetupmatsolvertype_(PC pc, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFactorSetUpMatSolverType(
	(PC)PetscToPointer((pc) ));
}
PETSC_EXTERN void  pcfactorsetzeropivot_(PC pc,PetscReal *zero, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFactorSetZeroPivot(
	(PC)PetscToPointer((pc) ),*zero);
}
PETSC_EXTERN void  pcfactorsetshifttype_(PC pc,MatFactorShiftType *shifttype, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFactorSetShiftType(
	(PC)PetscToPointer((pc) ),*shifttype);
}
PETSC_EXTERN void  pcfactorsetshiftamount_(PC pc,PetscReal *shiftamount, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFactorSetShiftAmount(
	(PC)PetscToPointer((pc) ),*shiftamount);
}
PETSC_EXTERN void  pcfactorsetdroptolerance_(PC pc,PetscReal *dt,PetscReal *dtcol,PetscInt *maxrowcount, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFactorSetDropTolerance(
	(PC)PetscToPointer((pc) ),*dt,*dtcol,*maxrowcount);
}
PETSC_EXTERN void  pcfactorgetzeropivot_(PC pc,PetscReal *pivot, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLREAL(pivot);
*ierr = PCFactorGetZeroPivot(
	(PC)PetscToPointer((pc) ),pivot);
}
PETSC_EXTERN void  pcfactorgetshiftamount_(PC pc,PetscReal *shift, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLREAL(shift);
*ierr = PCFactorGetShiftAmount(
	(PC)PetscToPointer((pc) ),shift);
}
PETSC_EXTERN void  pcfactorgetshifttype_(PC pc,MatFactorShiftType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFactorGetShiftType(
	(PC)PetscToPointer((pc) ),type);
}
PETSC_EXTERN void  pcfactorgetlevels_(PC pc,PetscInt *levels, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLINTEGER(levels);
*ierr = PCFactorGetLevels(
	(PC)PetscToPointer((pc) ),levels);
}
PETSC_EXTERN void  pcfactorsetlevels_(PC pc,PetscInt *levels, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFactorSetLevels(
	(PC)PetscToPointer((pc) ),*levels);
}
PETSC_EXTERN void  pcfactorsetallowdiagonalfill_(PC pc,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFactorSetAllowDiagonalFill(
	(PC)PetscToPointer((pc) ),*flg);
}
PETSC_EXTERN void  pcfactorgetallowdiagonalfill_(PC pc,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFactorGetAllowDiagonalFill(
	(PC)PetscToPointer((pc) ),flg);
}
PETSC_EXTERN void  pcfactorreorderfornonzerodiagonal_(PC pc,PetscReal *rtol, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFactorReorderForNonzeroDiagonal(
	(PC)PetscToPointer((pc) ),*rtol);
}
PETSC_EXTERN void  pcfactorsetmatsolvertype_(PC pc,char *stype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
/* insert Fortran-to-C conversion for stype */
  FIXCHAR(stype,cl0,_cltmp0);
*ierr = PCFactorSetMatSolverType(
	(PC)PetscToPointer((pc) ),_cltmp0);
  FREECHAR(stype,_cltmp0);
}
PETSC_EXTERN void  pcfactorgetmatsolvertype_(PC pc,char *stype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFactorGetMatSolverType(
	(PC)PetscToPointer((pc) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for stype */
*ierr = PetscStrncpy(stype, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, stype, cl0);
}
PETSC_EXTERN void  pcfactorsetfill_(PC pc,PetscReal *fill, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFactorSetFill(
	(PC)PetscToPointer((pc) ),*fill);
}
PETSC_EXTERN void  pcfactorsetuseinplace_(PC pc,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFactorSetUseInPlace(
	(PC)PetscToPointer((pc) ),*flg);
}
PETSC_EXTERN void  pcfactorgetuseinplace_(PC pc,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFactorGetUseInPlace(
	(PC)PetscToPointer((pc) ),flg);
}
PETSC_EXTERN void  pcfactorsetmatorderingtype_(PC pc,char *ordering, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
/* insert Fortran-to-C conversion for ordering */
  FIXCHAR(ordering,cl0,_cltmp0);
*ierr = PCFactorSetMatOrderingType(
	(PC)PetscToPointer((pc) ),_cltmp0);
  FREECHAR(ordering,_cltmp0);
}
PETSC_EXTERN void  pcfactorsetcolumnpivot_(PC pc,PetscReal *dtcol, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFactorSetColumnPivot(
	(PC)PetscToPointer((pc) ),*dtcol);
}
PETSC_EXTERN void  pcfactorsetpivotinblocks_(PC pc,PetscBool *pivot, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFactorSetPivotInBlocks(
	(PC)PetscToPointer((pc) ),*pivot);
}
PETSC_EXTERN void  pcfactorsetreusefill_(PC pc,PetscBool *flag, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCFactorSetReuseFill(
	(PC)PetscToPointer((pc) ),*flag);
}
#if defined(__cplusplus)
}
#endif
